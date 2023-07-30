from typing import List, Tuple
from correction import Correction
from steps.preprocessing import Preprocessing
from steps.res import Alphabet_resource, Correction_resource, Transliteration_resource
from transliteration import Transliteration
from steps.clusters import Clusters
from config.paths import *
from steps.utterance import Utterance
from utils.utils import Utils


class DatasetProject(Utils):
    def __init__(
        self, title: str = "main", num_files: int = 0, quiet: bool = False
    ) -> None:
        super().__init__(title, num_files, quiet)
        self.__init_res()
        self.__init_classes()
        self.__init_vars()

    def __init_classes(self, num_files: int = 0) -> None:
        self.set_num_files(num_files)
        self.p = Preprocessing(num_files=num_files)
        self.u = Utterance(num_files=num_files)
        self.c = Correction(num_files=num_files)
        self.t = Transliteration(num_files=num_files)

    def __init_vars(self):
        self.s550_utts = dict()
        self.bn_utts = dict()
        self.mm_utts = dict()

    def __init_res(self):
        cr = Correction_resource()
        tr = Transliteration_resource()
        ar = Alphabet_resource()

    @staticmethod
    def build_path(file_path: Path, dir: Path, extension: str = "txt"):
        return dir / f"{file_path.stem}.{extension}"

    

    # ! This will overwrite existing files, take care!!!
    # @staticmethod
    # def build_raw_dir():
    #     files = DatasetProject.get_files(dir=RTF_DATA, extension="rtf")
    #     for file_path in files:
    #         DatasetProject.write_text_file(
    #             content="",
    #             file_path=DatasetProject.build_path(file_path=file_path, dir=RAW_DATA),
    #         )

    def run(self, rtf: bool = False):
        if rtf:
            files = self.get_files(dir=RTF_DATA, extension="rtf")
        else:
            files = self.get_files(dir=RAW_DATA)

        # Step 0: Preprocessing
        self.__init_classes(len(files))
        for idx, file_path in enumerate(files):
            content = self.p.preprocess_file(file_path=file_path, idx=idx)
            self.write_text_file(
                content=content,
                file_path=self.build_path(file_path=file_path, dir=SCP_S550_DIR),
            )

        # Step 1: Utterances
        files = self.get_files(dir=SCP_S550_DIR)
        for idx, file_path in enumerate(files):
            content = self.u.utterance_file(file_path=file_path, idx=idx)
            self.write_text_file(
                content=content,
                file_path=self.build_path(file_path=file_path, dir=UTT_S550_DIR),
            )
            self.s550_utts.update(self.u.utt_content_to_dict(content))

        # Step 1.1: Write s550 text
        self.display(
            title=self.u.title, target=TEXT_S550_FILE.as_posix(), desc="saving"
        )
        self.write_text_file(
            content=self.u.utt_dict_to_content(self.s550_utts), file_path=TEXT_S550_FILE
        )

        # Step 1.2: Write s550 words
        utterances = self.u.get_utterances_from_text(file_path=TEXT_S550_FILE)
        words = sorted(set(utterances.split()))
        self.display(
            title=self.u.title, target=WORDS_S550_FILE.as_posix(), desc="saving"
        )
        self.write_text_file(content="\n".join(words), file_path=WORDS_S550_FILE)

        # Step 1.3: Write s550 chars
        chars = sorted(set(utterances))
        self.display(
            title=self.u.title, target=CHARS_S550_FILE.as_posix(), desc="saving"
        )
        self.write_text_file(content="\n".join(chars), file_path=CHARS_S550_FILE)

        # Step 2: Correction
        # Step 2.0.1: Correction of Scripts
        files = self.get_files(dir=SCP_S550_DIR)
        for idx, file_path in enumerate(files):
            content = self.c.correct_file(file_path=file_path, idx=idx)
            self.write_text_file(
                content=content,
                file_path=self.build_path(file_path=file_path, dir=SCP_BN_DIR),
            )

        # Step 2.0.2: Correction of Utterances
        files = self.get_files(dir=UTT_S550_DIR)
        for idx, file_path in enumerate(files):
            content = self.c.correct_file(file_path=file_path, idx=idx, is_utt=True)
            self.write_text_file(
                content=content,
                file_path=self.build_path(file_path=file_path, dir=UTT_BN_DIR),
            )
            self.bn_utts.update(self.u.utt_content_to_dict(content))

        # Step 2.1: Write bn text
        self.display(title=self.u.title, target=TEXT_BN_FILE.as_posix(), desc="saving")
        self.write_text_file(
            content=self.u.utt_dict_to_content(self.bn_utts), file_path=TEXT_BN_FILE
        )

        # Step 2.2: Write bn words
        utterances = self.u.get_utterances_from_text(file_path=TEXT_BN_FILE)
        words = sorted(set(utterances.split()))
        bn_words = words
        self.display(title=self.u.title, target=WORDS_BN_FILE.as_posix(), desc="saving")
        self.write_text_file(content="\n".join(words), file_path=WORDS_BN_FILE)

        # Step 2.3: Write bn chars
        chars = sorted(set(utterances))
        self.display(title=self.u.title, target=CHARS_BN_FILE.as_posix(), desc="saving")
        self.write_text_file(content="\n".join(chars), file_path=CHARS_BN_FILE)

        # Step 3: Transliteration
        # Step 3.0.1: Transliteration of Scripts
        files = self.get_files(dir=SCP_BN_DIR)
        for idx, file_path in enumerate(files):
            content = self.t.transliterate_file(file_path=file_path, idx=idx)
            self.write_text_file(
                content=content,
                file_path=self.build_path(file_path=file_path, dir=SCP_MM_DIR),
            )

        # Step 3.0.2: Transliteration of Utterances
        files = self.get_files(dir=UTT_BN_DIR)
        for idx, file_path in enumerate(files):
            content = self.t.transliterate_file(
                file_path=file_path, idx=idx, is_utt=True
            )
            self.write_text_file(
                content=content,
                file_path=self.build_path(file_path=file_path, dir=UTT_MM_DIR),
            )
            self.mm_utts.update(self.u.utt_content_to_dict(content))

        # Step 3.1: Write mm text
        self.display_line(
            title=self.u.title, target=TEXT_MM_FILE.as_posix(), suffix="saving"
        )
        self.write_text_file(
            content=self.u.utt_dict_to_content(self.mm_utts), file_path=TEXT_MM_FILE
        )
        # Step 3.2: Write mm words
        utterances = self.u.get_utterances_from_text(file_path=TEXT_MM_FILE)
        words = sorted(set(utterances.split()))
        self.display_line(
            title=self.u.title, target=WORDS_MM_FILE.as_posix(), suffix="saving"
        )
        self.write_text_file(content="\n".join(words), file_path=WORDS_MM_FILE)

        # Step 3.3: Write mm chars
        chars = sorted(set(utterances))
        self.display_line(
            title=self.u.title, target=CHARS_MM_FILE.as_posix(), suffix="saving"
        )
        self.write_text_file(content="\n".join(chars), file_path=CHARS_MM_FILE)

        # Step 4: Extra
        # Step 4.1: Generate WordMap
        # Step 4.1.1: Generate S550_BN WordMap
        self.generate_wordmap(
            file_path=WORDS_S550_FILE, fun=self.c.correct, lang1=S550, lang2=BN
        )
        # Step 4.1.2: Generate BN_MM WordMap
        self.generate_wordmap(
            file_path=WORDS_BN_FILE, fun=self.t.transliterate, lang1=BN, lang2=MM
        )
        # Step 4.2 Generate Clusters Info
        self.generate_clusters_info(bn_words=bn_words)

    @staticmethod
    def generate_wordmap(file_path: Path, fun, lang1: str, lang2: str):
        content = DatasetProject.read_encoded_file(file_path)
        wmap = {word: fun(word) for word in content.split("\n")}
        output_filename = f"{lang1}_{lang2}"
        DatasetProject.write_json_file(
            data=wmap, file_path=WORD_MAP_DIR / output_filename
        )
        DatasetProject.write_csv_file(
            data=wmap,
            fieldnames=(lang1, lang2),
            file_path=WORD_MAP_DIR / output_filename,
        )

    @staticmethod
    def generate_clusters_info(bn_words: List[str]):
        # Step 4.2.1: Build clusters
        clusters = Clusters.get_clusters(content="\n".join(bn_words))
        clusters = sorted(clusters)
        Utils.display_line(
            title="clusters",
            target=CLUSTERS_FILE.as_posix(),
            suffix="writing-clusters-file",
        )
        DatasetProject.write_text_file(
            content="\n".join(clusters), file_path=CLUSTERS_FILE
        )

        # Step 4.2.2: Build clusters with examples
        clusters_egs = Clusters.build_egs(
            content="\n".join(bn_words), clusters=clusters
        )
        Utils.display_line(
            title="clusters",
            target=CLUSTERS_EGS_FILE.as_posix(),
            suffix="writing-clusters-examples-file",
        )
        DatasetProject.write_json_file(data=clusters_egs, file_path=CLUSTERS_EGS_FILE)
        DatasetProject.write_json_file(
            data=clusters_egs, file_path=CLUSTERS_EGS_FILE, unicode=True
        )

        # Step 4.2.3: Build clusters map
        clusters_map = Clusters.build_probable_map(clusters=clusters)
        Utils.display_line(
            title="clusters",
            target=CLUSTERS_MAP_FILE.as_posix(),
            suffix="writing-clusters-map-file",
        )
        DatasetProject.write_json_file(data=clusters_map, file_path=CLUSTERS_MAP_FILE)
        DatasetProject.write_json_file(
            data=clusters_map, file_path=CLUSTERS_MAP_FILE, unicode=True
        )

        # Step 4.2.4: Build detailed cluster dictionary
        clusters_detailed, clusters_pct = Clusters.build_detailed_clusters(
            cluster_egs=clusters_egs, total_words=len(bn_words)
        )
        Utils.display_line(
            title="clusters",
            target=CLUSTERS_DETAILED_FILE.as_posix(),
            suffix="writing-clusters-detailed-file",
        )
        DatasetProject.write_json_file(
            data=clusters_detailed, file_path=CLUSTERS_DETAILED_FILE
        )
        DatasetProject.write_json_file(
            data=clusters_detailed,
            file_path=CLUSTERS_DETAILED_FILE,
            unicode=True,
        )
        DatasetProject.write_json_file(data=clusters_pct, file_path=CLUSTERS_PCT_FILE)
        DatasetProject.write_json_file(
            data=clusters_pct, file_path=CLUSTERS_PCT_FILE, unicode=True
        )