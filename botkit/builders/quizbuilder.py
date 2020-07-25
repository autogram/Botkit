from typing import List, Optional, Dict, Any


class QuizBuilder:
    def __init__(self):
        self.question: str = "Untitled Quiz"
        self._options: List[str] = []
        self._is_anonymous: bool = True
        self._correct_option_id: Optional[int] = None

    def add_option(self, name: str, is_correct_answer: bool = None):
        if is_correct_answer is True:
            self._correct_option_id = len(self._options)
        self._options.append(name)
        return self

    def set_anonymous(self):
        self._is_anonymous = True
        return self

    def set_public(self):
        self._is_anonymous = False
        return self

    def set_question(self, title: str):
        self.question = title
        return self

    @property
    def title(self):
        return self.question

    @title.setter
    def title(self, value):
        self.question = value

    def render(self) -> Dict[str, Any]:
        return dict(
            question=self.question,
            options=self._options,
            is_anonymous=self._is_anonymous,
            allows_multiple_answers=False,
            type="quiz",
            correct_option_id=self._correct_option_id,
        )