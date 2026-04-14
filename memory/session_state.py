class SessionState:
    def __init__(self, max_turns=2):
        self.chat_history = []
        self.working_context = None
        self.max_turns = max_turns

    def update_history(self, user_input, assistant_output):
        self.chat_history.append({
            "role": "user",
            "content": user_input
        })

        self.chat_history.append({
            "role": "assistant",
            "content": assistant_output
        })

        if len(self.chat_history) > self.max_turns * 2:
            self.chat_history = self.chat_history[-self.max_turns * 2:]