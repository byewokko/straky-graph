import straky


def main():
	b = straky.Board(4)
	b.play_game(players=[straky.player.PlayerRandom(), straky.player.PlayerTextInput()])


if __name__ == "__main__":
	main()
