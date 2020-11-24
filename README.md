# Number_baseball_game
- with socket programming(local host)
(Computer Network class project assignment)

Rules of the Number Baseball Game
- There are two players: 1) server player and 2) client player.
- Each player chooses 3-digit number at random, each of digit is between 1 and 9. (‘0’ is excluded.)
These three digits must be different from each other. (e.g., ‘113’ is not possible.)
- Each player guesses the number of other player by saying 3-digit guessing number in turn. These
three digits must also be different from each other. (e.g., ‘113’ is not possible.)
- For the guessed number, each player must inform the result by counting the number of strikes
and balls. When a guessed digit is the same as the answer digit with the same position, it is called
“strike”. When a guessed digit is the same as the answer digit but the position is different, it is
called “ball”. For example, the client player guessed the number as ‘435’ and the answer number of
the server player is ‘365’. The server player must inform to the client player that there are 1 strike
and 1 ball.
- The client player starts a guess first, but the server player will have the same number of chances
for guessing numbers.
- Type of game results
• Client Win: The client player guessed the right answer but the server player could not.
• Server Win: The server player guessed the right answer but the client player could not.
• Draw: Both the client player and the server player guessed the right answers.
