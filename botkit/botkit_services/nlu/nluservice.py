from abc import ABCMeta, abstractmethod
import dateutil.parser
from datetime import datetime
from pprint import pprint
from typing import Dict

from dialogflow_v2 import SessionsClient
from dialogflow_v2.proto.session_pb2 import (
    DetectIntentResponse,
    QueryInput,
    QueryResult,
    TextInput,
)
from haps import SINGLETON_SCOPE, base, egg, scope
from haps.config import Config

from botkit.botkit_services.nlu.dialogflowconfig import DialogflowConfig
from botkit.botkit_services.nlu.messageunderstanding import MessageUnderstanding


@scope(SINGLETON_SCOPE)
@base
class INLUService(ABC):
    @abstractmethod
    def detect_intents(self, chat_id: int, message: str, language_code: str = None):
        pass


@egg
class DialogflowService(INLUService):
    config: DialogflowConfig = Config(DialogflowConfig.KEY)

    def __init__(self):
        self.session_client = SessionsClient.from_service_account_file(
            self.config.json_credentials_file
        )

    def detect_intents(
        self, chat_id: int, message: str, language_code: str = "en"
    ) -> MessageUnderstanding:
        session = self.session_client.session_path(self.config.project_id, chat_id)

        text_input = TextInput(text=message, language_code=language_code)

        query_input = QueryInput(text=text_input)

        response: DetectIntentResponse = self.session_client.detect_intent(
            session=session, query_input=query_input
        )
        result: QueryResult = response.query_result

        # Ignored result fields:
        #   - all_required_params_present
        #   - fulfillment_text
        #   - fulfillment_messages
        #   - webhook_source
        #   - webhook_payload
        #   - output_contexts
        #   - diagnostic_info

        return MessageUnderstanding(
            text=result.query_text,
            language_code=result.language_code,
            action=result.action,
            intent=result.intent.display_name,
            parameters=self._normalize_parameters(result.parameters),
            contexts=result.output_contexts,
            confidence=result.speech_recognition_confidence
            or result.intent_detection_confidence,
            date=datetime.now(),
        )

    def _normalize_parameters(self, params: Dict):
        result = {}
        for k, v in params.items():

            if "date" in k and v:
                if hasattr(v, "keys") and "date_time" in v:
                    accessor = v["date_time"]
                else:
                    accessor = v
                print(accessor)
                time_and_date: datetime = dateutil.parser.parse(accessor)
                result[k] = time_and_date
                continue

            result[k] = v

        return result


if __name__ == "__main__":
    conf = DialogflowConfig(
        project_id="userbot-9994a",
        json_credentials_file="C:/projects/userbot/dialogflow-credentials.json",
    )
    c = DialogflowService(conf)
    nlu = c.detect_intents(123, "!remind @tWiTfAcE to buy milk tomorrow at 6", "en")
    # print(nlu)
    pprint(nlu)
