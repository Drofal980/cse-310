use rayon::prelude::*;
use std::collections::HashMap;
use std::env;
use std::error::Error;
use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

/// A record parsed from the CSV: a 5-letter word and its numeric weight.
#[derive(Debug, Clone)]
struct WordRecord {
    word: String, // stored lowercase
    weight: f64,  // numeric weight (e.g., 58.0)
}

/// Type alias: for each of the 5 positions we keep a HashMap letter -> score
type PosMaps = [HashMap<char, f64>; 5];

/// Create an empty PosMaps (helper)
fn empty_pos_maps() -> PosMaps {
    [
        HashMap::new(),
        HashMap::new(),
        HashMap::new(),
        HashMap::new(),
        HashMap::new(),
    ]
}

/// Parse a single CSV line like "ABACK,58%" or "ABASE,51.22%".
/// Returns None for malformed lines.
fn parse_line(line: &str) -> Option<WordRecord> {
    let mut parts = line.split(',');
    let word = parts.next()?.trim();
    let weight_str = parts.next()?.trim();

    if word.len() != 5 {
        return None;
    }

    // Remove trailing percent sign if present and parse as f64
    let weight_clean = weight_str.trim_end_matches('%');
    let weight: f64 = weight_clean.parse().ok()?;

    Some(WordRecord {
        word: word.to_lowercase(),
        weight,
    })
}

/// Load CSV file (simple line-based parser). Ignores lines that don't parse.
fn load_csv<P: AsRef<Path>>(path: P) -> Result<Vec<WordRecord>, Box<dyn Error>> {
    let file = File::open(path)?;
    let reader = io::BufReader::new(file);
    let mut out = Vec::new();

    for line_res in reader.lines() {
        let line = line_res?;
        if let Some(rec) = parse_line(&line) {
            out.push(rec);
        }
    }
    Ok(out)
}

/// Compute weighted letter scores per position in parallel.
///
/// Strategy:
/// - Use `par_iter()` to map each WordRecord to a local PosMaps contribution.
/// - Collect partial PosMaps into a Vec and then fold them into a single PosMaps.
/// This avoids shared mutable state and uses thread-local HashMaps.
fn compute_weights_parallel(records: &[WordRecord]) -> PosMaps {
    let partials: Vec<PosMaps> = records
        .par_iter()
        .map(|r| {
            let mut pm = empty_pos_maps();
            for (i, ch) in r.word.chars().enumerate().take(5) {
                *pm[i].entry(ch).or_insert(0.0) += r.weight;
            }
            pm
        })
        .collect();

    partials.into_iter().fold(empty_pos_maps(), |mut acc, pm| {
        for (i, map) in pm.into_iter().enumerate() {
            for (ch, v) in map {
                *acc[i].entry(ch).or_insert(0.0) += v;
            }
        }
        acc
    })
}

/// Return the top N letters (char, score) for each position, sorted descending by score.
fn top_letters_per_position(pos_maps: &PosMaps, top_n: usize) -> Vec<Vec<(char, f64)>> {
    (0..5)
        .map(|i| {
            let mut v: Vec<(char, f64)> = pos_maps[i].iter().map(|(&c, &s)| (c, s)).collect();
            v.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
            v.into_iter().take(top_n).collect()
        })
        .collect()
}

/// Compute a HashMap of word -> score using the provided PosMaps.
/// Score for a word = sum over positions (pos_maps[i].get(letter).unwrap_or(0.0))
///
/// - `pos_maps` is borrowed; function does not take ownership.
/// - `records` is borrowed; we clone the word string for the map keys.
fn compute_word_scores(pos_maps: &PosMaps, records: &[WordRecord]) -> HashMap<String, f64> {
    // Compute (word, score) pairs in parallel, collect into a Vec
    let pairs: Vec<(String, f64)> = records
        .par_iter()
        .map(|r| {
            let score: f64 = r
                .word
                .chars()
                .enumerate()
                .take(5)
                .map(|(i, ch)| pos_maps[i].get(&ch).copied().unwrap_or(0.0))
                .sum();
            (r.word.clone(), score)
        })
        .collect();

    // Convert Vec<(String,f64)> into HashMap<String,f64>
    pairs.into_iter().collect()
}

/// Return the top `top_n` words sorted by descending score.
/// This computes scores (in parallel), sorts them (sequential), and returns the top slice.
fn top_words_by_score(
    pos_maps: &PosMaps,
    records: &[WordRecord],
    top_n: usize,
) -> Vec<(String, f64)> {
    // Compute pairs in parallel (same as compute_word_scores)
    let mut pairs: Vec<(String, f64)> = records
        .par_iter()
        .map(|r| {
            let score: f64 = r
                .word
                .chars()
                .enumerate()
                .take(5)
                .map(|(i, ch)| pos_maps[i].get(&ch).copied().unwrap_or(0.0))
                .sum();
            (r.word.clone(), score)
        })
        .collect();

    // Sort descending by score (use stable sort if you want deterministic tie-breaking)
    pairs.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());

    // Return top_n (or fewer if not enough words)
    pairs.into_iter().take(top_n).collect()
}

/// Check whether `input` is among the top `top_n` words by score.
/// If yes, return the top-list entry (word, score) and `true`.
/// If not, compute the score for `input` (even if it's not in `records`) and return it with `false`.
///
/// - `pos_maps` : per-position letter -> score maps
/// - `records`  : list of WordRecord used to compute top words
/// - `input`    : user-provided word (any case)
/// - `top_n`    : how many top words to consider
///
/// Returns `Ok((word_string, score, was_in_top))` or `Err(&'static str)` for invalid input.
fn top_or_score_word(
    pos_maps: &PosMaps,
    records: &[WordRecord],
    input: &str,
    top_n: usize,
) -> Result<(String, f64, bool), &'static str> {
    // Normalize input
    let w = input.trim().to_lowercase();

    // Validate length
    if w.chars().count() != 5 {
        return Err("word must be exactly 5 letters");
    }

    // Compute top words (this will compute scores for all words and sort)
    let top_words = top_words_by_score(pos_maps, records, top_n);

    // Check if the normalized input is present among the top words
    if let Some((word, score)) = top_words
        .iter()
        .find(|(word, _score)| word.as_str() == w.as_str())
    {
        // Found in top list — return the top-list entry and true
        return Ok((word.clone(), *score, true));
    }

    // Not found in top list — compute score for arbitrary input
    let score: f64 = w
        .chars()
        .enumerate()
        .take(5)
        .map(|(i, ch)| pos_maps[i].get(&ch).copied().unwrap_or(0.0))
        .sum();

    Ok((w, score, false))
}

/// Pretty-print the full maps (for debugging) and the top letters.
fn print_results(pos_maps: &PosMaps, top_n: usize) {
    println!("Top {} letters per position (1..5):", top_n);
    let tops = top_letters_per_position(pos_maps, top_n);
    for (i, list) in tops.iter().enumerate() {
        let formatted: Vec<String> = list
            .iter()
            .map(|(c, s)| format!("{}:{:.2}", c, s))
            .collect();
        println!("  Position {}: {}", i + 1, formatted.join(", "));
    }
}

fn main() -> Result<(), Box<dyn Error>> {
    // READ FILE
    // Parse command-line arguments to get CSV path (default: "wordle-answers.csv") 
    // Given CSV from https://wordletools.azurewebsites.net/weightedbottles
    let default_path = "..\\wordle-answers.csv";
    let args: Vec<String> = env::args().collect();
    let path = args
        .get(1)
        .map(|s| s.as_str())
        .unwrap_or(default_path);

    println!("Loading CSV from: {}", path);
    let records = load_csv(path)?;
    println!("Loaded {} valid 5-letter records.", records.len());
    println!();

    // CALCULATE SCORES FOR LETTERS
    // Compute weights in parallel
    let pos_maps = compute_weights_parallel(&records);

    // Print top n letters for each position
    let top_n_letters = 10;
    print_results(&pos_maps, top_n_letters);
    println!();

    // CALCULATE SCORES FOR WORDS
    let word_scores_map = compute_word_scores(&pos_maps, &records);
    println!("Computed scores for {} words.", word_scores_map.len());

    // show top n words
    let top_n_words = 5;
    let top20 = top_words_by_score(&pos_maps, &records, top_n_words);
    println!("Top {} candidate words by score:", top_n_words);
    for (rank, (word, score)) in top20.into_iter().enumerate() {
        println!(
            "{:2}. {:5}  score: {:.3}",
            rank + 1,
            word.to_uppercase(),
            score
        );
    }

    // CALCULATE SCORE FOR USER-INPUT WORD
    // let input_word = "salet"; // or read from CLI / prompt
    println!("\nEnter a word");
    let mut input_word = String::new();
    io::stdin().read_line(&mut input_word)?;
    let input_word = input_word.trim();
    match top_or_score_word(&pos_maps, &records, input_word, top_n_words) {
        Ok((word, score, true)) => {
            println!("'{}' is in the top {} (score {:.3}). Returning top entry.", word.to_uppercase(), top_n_words, score);
        }
        Ok((word, score, false)) => {
            println!("'{}' is NOT in the top {}. Computed score: {:.3}", word.to_uppercase(), top_n_words, score);
        }
        Err(e) => {
            println!("Invalid input: {}", e);
        }
    }

    Ok(())
}

// fn hello_world() {
//     // This function prints "Hello, world!" to the console.
//     println!("Hello, world!");
// }
