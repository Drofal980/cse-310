#!/usr/bin/env kotlin

data class Flashcard(
    val question: String,
    val answer: String
)

fun createFlashcard(): Flashcard {
    println("What is the question?")
    val question = readln()
    println("What is the answer?")
    val answer = readln()

    val newFlashcard = Flashcard(question, answer)
    return newFlashcard
}

fun saveCards(flashcards: List<Flashcard>) {
    println("Saving ${flashcards.size} flashcards...")
    val filename = "flashcards.txt"
    val file = java.io.File(filename)
    file.printWriter().use { out ->
        flashcards.forEach { card ->
            out.println("${card.question}|${card.answer}")
        }
    }   
    println("All flashcards saved.")
}

fun loadCards(): MutableList<Flashcard> {
    val flashcards: MutableList<Flashcard> = mutableListOf()
    val filename = "flashcards.txt"
    val file = java.io.File(filename)

    if (!file.exists()) {
        println("No saved flashcards found.")
        return flashcards
    }

    file.forEachLine { line ->
        val parts = line.split("|")
        if (parts.size == 2) {
            val question = parts[0]
            val answer = parts[1]
            flashcards.add(Flashcard(question, answer))
        }
    }

    println("Loaded ${flashcards.size} flashcards.")
    return flashcards
}

fun menu(){
    var flashcards:  MutableList<Flashcard> = mutableListOf()
    var done: Boolean = false
    while (!done) {
        println("-----------------------")
        println("Select an option: ")
        println("1. Create a new card")
        println("2. Start Quiz")
        println("3. Load Cards")
        println("4. Save and Quit")
        println("5. Quit")
        println("-----------------------")
        // take input from user
        val input = readln()

        when (input) {
            "1" -> flashcards.add(createFlashcard())
            "2" -> quiz(flashcards)
            "3" -> flashcards = loadCards()
            "4" -> saveCards(flashcards).also { done = true }
            "5" -> done = true
            else -> println("Invalid input.")
        }

    }

}

fun quiz(quizCards : List<Flashcard>) {
    var score = 0

    // Shuffle Cards
    val shuffledQuizCards = quizCards.shuffled()
    // Start Quiz
    for (card in shuffledQuizCards) {
        println(card.question)
        print("Your answer: ")
        val userInput = readln()

        if (userInput == "quit") {
            println("Quitting Quiz...")
        }

        if (userInput.equals(card.answer, ignoreCase = true)) {
            println("Correct!\n")
            score++
        } else {
            println("Incorrect. The correct answer is: ${card.answer}\n")
        }
    }

    println("Quiz Results:")
    println("Your score: $score / ${shuffledQuizCards.size}")
}

fun main(){
    menu()
}

main()