# Wordle Helper

This is a simple command-line tool to help show the top letters in each of the 5 positions in Wordle, based on a list of possible Wordle answers. It also calculates the words that have the highest total letter frequency, which can be used as good guesses in Wordle.

## Instructions for Build and Use

Steps to build and/or run the software:

1. Download the source code and navigate to the project directory, going into the wordle-helper directory.
2. Build the project using the Rust compiler with the command `cargo build`.

Instructions for using the software:

1. Run the compiled binary with the command `cargo run` to see the top letters in each position and the best guesses based on letter frequency.
2. You can then input a 5-letter word to find it's custom score based on the letter frequencies, which can help you decide if it's a good guess in Wordle.

## Development Environment

To recreate the development environment, you need the following software and/or libraries with the specified versions:

* Download and install Rust from the official website: https://www.rust-lang.org/tools/install
* Make sure you have the latest version of Rust installed by running `rustc --version` in your terminal.

## Useful Websites to Learn More

I found these websites useful in developing this software:

* [Reference Project](https://github.com/petertseng/wordle-rs/tree/master)
* [Possible Wordle Answers](https://gist.github.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b)
* [Weight of Wordle Answers](https://wordletools.azurewebsites.net/weightedbottles?SortOrder=Alphabetical&submit=Submit)

## Future Work

The following items I plan to fix, improve, and/or add to this project in the future:

* [ ] Add functionality to filter the list of possible answers based on user input of correct and incorrect letters.
* [ ] Implement a more advanced scoring system that takes into account letter positions and common letter combinations in English words.
* [ ] Create a graphical user interface (GUI) for easier interaction and visualization of the letter frequencies and best guesses.