from datetime import datetime
from chatbot import TxtChatBot


def main():
    """
    'Chatbot' assistant with CLI Interface
    """

    print("\nHello! I am a chatbot. I can answer questions based on the content of a your documents.\n")

    chatbot = TxtChatBot()
    chatbot.init_chatbot()

    while True:
        current_datetime = datetime.now()
        user_input = input("Do you have any questions? To exit, type 'bye': ")

        answer = chatbot.generate_response(user_input)
        elapsed_time = datetime.now() - current_datetime

        print("\nChatbot: ", answer)
        print("\n Time elapsed: ", elapsed_time.total_seconds(), "seconds \n")

        if user_input.lower() == "bye":
            break


if __name__ == '__main__':
    main()
