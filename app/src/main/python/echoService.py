import Message

def echo (message: Message) -> Message:
    print("Received message body [", message.body, "] from [", message.sender, "].")
    return message