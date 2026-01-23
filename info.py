from wyoming.info import Describe, Info, Attribution


def create_describe() -> Describe:
    return Describe(
        info=Info(
            name="FunASR paraformer-zh",
            description="FunASR paraformer-zh via Wyoming",
            version="1.0.0",
            languages=["zh-CN"],
            attribution=Attribution(
                name="FunASR",
                url="https://github.com/alibaba-damo-academy/FunASR",
            ),
        )
    )
