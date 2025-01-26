import re
from playsound import playsound
import ChatTTS
import torch
import torchaudio
from typing import Optional
import os
import uuid
import cn2an


class TTSModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TTSModel, cls).__new__(cls)
            cls._instance.chat = ChatTTS.Chat()
            cls._instance.chat.load(compile=True)  # 提高性能(使用GPU时需要关闭)
            print("模型已加载")
        return cls._instance

    @classmethod
    def load_model(cls):
        """加载模型的函数，在外部调用时可以提前加载。"""
        tts_model = cls._instance.chat if cls._instance else TTSModel().chat
        tts_model.load(compile=False)  # 提高性能(使用GPU时需要关闭)
        print("TTS 模型已加载")


def generate_tts_audio(
        text: str,
        output_file: str,
        spk_emb: Optional[str] = None,
        temperature: float = 0.3,
        sample_rate: int = 24000
):
    """
    生成指定文本的语音并保存为音频文件。

    参数:
        text (str): 要生成语音的文本。
        output_file (str): 生成的语音文件路径。
        spk_emb (Optional[str]): 使用的音色嵌入，如果为空则随机生成。
        temperature (float): 控制生成的随机性，默认值为 0.3。
        sample_rate (int): 生成的语音的采样率，默认是 24000。
    """
    # 使用单例模式获取已加载的模型
    tts_model = TTSModel().chat

    check_txt = convert_numbers_to_chinese(text+'1')

    spk_static = ("蘁淰敍欀厃殐悎帄桗愨昛乜赔解掲囊昿疸粐案券廿櫉甮庖蝺屶櫳升歩揭盧惚蓷於罜耡捶耥覀虧洹贆尅戚旐缑詞孯殅怄査竐蝑癑堪紽晻蛊瞒彐"
                  "搼砦犑噋蚆欖廷稬媇愨溧恱朱劒睶脰椖娢罼潚嘈崷峧尅絑濁笥懘箜薑筫澠獏褙巛藟椒蒻昆妍烅廑乆簫舢孠譲窩晔士啞幅笊侅粌舴丈倭村揘剬"
                  "螁筅犷叟入簤江福幵櫍綂狻呦灳薬三求养贾艛憧橅趔瑭硏三傳締嚫甙砣榠哎蒶艋勿国茂臜獜室蔭啃筏矴枲豼苌摟挼冦聘莥蘟杌抯敡懭珁侌浑"
                  "袕膪藺氟怳叚揶捜啱笧潂晄砃兝晿聄诼箽祣斞嗷茛荧檙粗榈藥曁疁覢倭泐睔粲嶡审瞲櫾祁召猍斕脳梤噕咻嵥噗蓃笄圛尴覟羋塌捞文翑簦趙路"
                  "扟戛与毊舌懋穔呹愒訁瀰劁癎浠拋甥球繥裛妨賐彜糢椤唕漩寺傼偯疑葭纬証睿翜罈盞粘囡垉庲捽襛蚚薀枣洐媩咊瞊婯崶极狣珦仟割垄竛示汰"
                  "証珠解蘀朒笓褯唽烷叻禯氨謑盤圫葢乑盨祚星拆暣甇臙妿伕舆相牿楸忮渁褉萓玻硓氉噪儋烨咗殨匏兞海奊彃槎琫珰磡匡秀塮坌瀗觎瑌摹假衈"
                  "慨岛堄憓艐竓欵椰步蜦聆储之謐凵甉徜沓墥擻繿娊岺琕囊橣厼抁艉孲氬牔敋櫼楕豽反蛧嬷簔篤揾墣庉漲漧耛詨覧玄惬綈諍簧濶猜寽渟衇叢垗"
                  "誽試缺抰赘崭殘姖园惞梌渁穎擎睱祗蠖澜脩蚎峥吳巣跹棉揽唗漄觳崠瘥蔢扩解絔疈讚讦脹烲湀嵅犉旤憔歇廨掯岵埅箶纾勗尤市氐簅榠睴蒂恂"
                  "渴篅螻疄悂炇萖縍粈蔌仺睘俋趲蘡貘懻炕垆偼畃夺溥埚焈賂埮糡諡樠欧誧蠣槡挥暘神憤嚿埪悶旡漊吘訏晝涐綕帗独蜅孰潦蝘噵瘒讃膣眹纏潑"
                  "槸蛕劊譴檴暉覆丩圇溰謥朡坌柖皳芮臬聽亱剋娓赡楎櫩孖珜炃昚想洞熺哚眴褙絎奋屦纵蜾孝袟詷穏帍禈孠萛虐渮埓稌嗯掫牼棕怈诏爚烘蛳彙"
                  "悊薼佉帋讣揗俛繷崒獁儋珕詶虃堀庚覆誊堝劒肓漎訍罣牘菨紞恺眾熟升悚沍尴喞涷捵壴蓕粙宖溯漊伌掜篦尸厷衁橠兇茮椏檱汾謪讻缢嗂氂柰"
                  "婓嚟縁莁暰楘蝾屔数獭亸竳蜵濻昻蒂媅禸愢勩暏峘噋皰煗泥罜穖覝唉枩瘕趴俺葫池蔱纆盼椌烆汜勘柖慗硩潄璒丑涯崡才薗搣篮扰倬慾漹贳咧"
                  "凹瞸桟伀嘄將喞垽殯堺勮掸修傻忖伺棓痏滯谍捝滷杇诼暍撯趢穇袜礴妯噲泩批臟帩舳嬫巤欝私汷琦筮囁翽瀹産孼幗桡悞秋甂暜炬勧襽渲廦佨"
                  "久峭楍孺掶彺净双橀腩嶝熜牘犓涼誆詶趥荫抙氶糭肫蘊唞刋渦摐剕莆綁膈榵矉懹惸匋絑藸勄妨斸楢沀匌揕坤蛲夌摅椣胨营珝哿屭四棍叜熬呥敟冼一㴁")

    # 如果未提供音色嵌入，则随机生成一个
    if spk_emb is None:
        spk_emb = tts_model.sample_random_speaker()
    # print(spk_emb)
    # 设置生成的参数
    params_infer_code = ChatTTS.Chat.InferCodeParams(
        spk_emb=spk_static,  # 使用随机生成或指定的音色
        temperature=temperature,  # 自定义生成温度
    )

    # 生成语音
    wavs = tts_model.infer(check_txt, skip_refine_text=True, params_infer_code=params_infer_code)

    # 确保音频数据为 2D 张量 (channels, samples)
    wavs_tensor = torch.tensor(wavs[0]).unsqueeze(0)  # 在第 0 维添加一个维度，表示单声道

    # 保存生成的语音到文件
    torchaudio.save(output_file, wavs_tensor, sample_rate)

    return output_file


def convert_numbers_to_chinese(text_c):
    """将文本中的数字转换为中文数字，并去掉方括号"""

    # 替换文本中的数字为中文数字
    def replace_match(match):
        num = match.group(0)  # 获取匹配到的数字
        return cn2an.an2cn(num, "low")  # 转换为中文数字

    # 将所有数字转换为中文数字
    text_c = re.sub(r'\d+', replace_match, text_c)

    # 去掉方括号 []
    text_c = re.sub(r'[\[\]]', '', text_c)

    text_c = re.sub(r'？', '问号', text_c)

    return text_c

def play_audio_with_playsound(wav_file):
    playsound(wav_file)

if __name__ == '__main__':
    # 要生成语音的文本
    text = "你好，欢迎使用文本转语音系统。"

    # 创建输出目录
    output_dir = "output_audio"
    os.makedirs(output_dir, exist_ok=True)

    # 生成一个唯一的文件名
    unique_filename = f"{uuid.uuid4()}.mp3"
    output_file = os.path.join(output_dir, unique_filename)

    # 调用函数生成语音
    generated_file = generate_tts_audio(text, output_file)
    play_audio_with_playsound(output_file)
    # print(f"语音已生成并保存为: {generated_file}")
