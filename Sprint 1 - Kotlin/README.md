# Kotlin Flashcards Script

A simple script that allows user to create and review custom flashcards. The flashcards are stored in a text file, and the user can add new cards or review existing ones through a command-line interface.

## Instructions for Build and Use

Steps to build and/or run the software:

1. Download and install Kotlin from [the official website](https://kotlinlang.org/docs/command-line.html).
2. Add Kotlin to your system PATH to use it from the command line.
3. Run the script using the command: `kotlinc -script "PATH_TO_SCRIPT\flashcards.main.kts"` to execute.

Instructions for using the software:

1. Upon running the script, you will be presented with a menu to either add a new flashcard or review existing ones.
2. To add a new flashcard, select the "1" option and input the question and answer when prompted.
3. To review flashcards, select the "2" option. The script will display each question and allow the user to input their answer. When all flashcards have been reviewed, the user will see their overall score.
4. To exit the program and save your flashcards, select the "3" option.
5. To load existing flashcards from the file, select the "4" option.
6. To quit without saving, select the "5" option.

## Development Environment

To recreate the development environment, you need the following software and/or libraries with the specified versions:

* Kotlin 2.3.0 or higher
* A text editor or IDE that supports Kotlin (e.g., IntelliJ IDEA, Visual Studio Code)

## Useful Websites to Learn More

I found these websites useful in developing this software:

* [W3 Schools](https://www.w3schools.com/KOTLIN/index.php)
* [GitHub Examples](https://github.com/Kotlin/kotlin-examples)
* [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Future Work

The following items I plan to fix, improve, and/or add to this project in the future:

* [ ] Allow users to edit or delete existing flashcards.
* [ ] Implement a graphical user interface (GUI) for better user experience.
* [ ] Add functionality to categorize flashcards by subject or topic.
