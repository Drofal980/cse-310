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

fun menu(){
    var flashcards:  MutableList<Flashcard> = mutableListOf()
    var done: Boolean = false
    while (!done) {
        println("-----------------------")
        println("Select an option: ")
        println("1. Create a new card")
        println("2. Start Quiz")
        println("3. Quit")
        println("-----------------------")
        // take input from user
        val input = readln()

        when (input) {
            "1" -> flashcards.add(createFlashcard())
            "2" -> quiz(flashcards)
            "3" -> done = true
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