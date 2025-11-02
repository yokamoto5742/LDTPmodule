from database import get_engine, get_session_factory


def initialize_database():
    """テーブル作成"""
    from models import Base
    engine = get_engine()
    Base.metadata.create_all(engine)


def seed_initial_data():
    """初期データ投入"""
    from models import MainDisease, SheetName, Template

    Session = get_session_factory()
    session = Session()

    try:
        # MainDiseaseの初期データ
        if session.query(MainDisease).count() == 0:
            main_diseases = [
                MainDisease(id=1, name="高血圧症"),
                MainDisease(id=2, name="脂質異常症"),
                MainDisease(id=3, name="糖尿病")
            ]
            session.add_all(main_diseases)
            session.commit()

        # SheetNameの初期データ
        if session.query(SheetName).count() == 0:
            sheet_names = [
                SheetName(main_disease_id=1, name="1_血圧130-80以下"),
                SheetName(main_disease_id=1, name="2_血圧140-90以下"),
                SheetName(main_disease_id=1, name="3_血圧140-90以下_歩行"),
                SheetName(main_disease_id=2, name="1_LDL120以下"),
                SheetName(main_disease_id=2, name="2_LDL100以下"),
                SheetName(main_disease_id=2, name="3_LDL70以下"),
                SheetName(main_disease_id=3, name="1_HbA1c７％"),
                SheetName(main_disease_id=3, name="2_HbA1c６％"),
                SheetName(main_disease_id=3, name="3_HbA1c８％"),
            ]
            session.add_all(sheet_names)
            session.commit()

        # Templateの初期データ
        if session.query(Template).count() == 0:
            templates = [
                Template(main_disease="高血圧症", sheet_name="1_血圧130-80以下",
                         target_bp="130/80",
                         target_hba1c="",
                         goal1="家庭血圧が測定でき、朝と就寝前のいずれかで130/80mmHg以下",
                         goal2="塩分を控えた食事と運動習慣を目標にする",
                         diet1="塩分量を適正にする",
                         diet2="食物繊維の摂取量を増やす",
                         diet3="ゆっくり食べる",
                         diet4="間食を減らす",
                         exercise_prescription="ウォーキング", exercise_time="30分",
                         exercise_frequency="週に2日",
                         exercise_intensity="少し汗をかく程度", daily_activity="5000歩",
                         other1="睡眠の確保1日7時間", other2="毎日の歩数の測定"),
                Template(main_disease="高血圧症", sheet_name="2_血圧140-90以下",
                         goal1="家庭血圧が測定でき、朝と就寝前のいずれかで140/90mmHg以下",
                         goal2="塩分を控えた食事と運動習慣を目標にする",
                         target_bp="140/90",
                         target_hba1c="",
                         diet1="塩分量を適正にする",
                         diet2="食物繊維の摂取量を増やす",
                         diet3="ゆっくり食べる",
                         diet4="間食を減らす",
                         exercise_prescription="ストレッチ体操", exercise_time="30分",
                         exercise_frequency="週に2日",
                         exercise_intensity="少し汗をかく程度", daily_activity="ストレッチ運動を主に行う",
                         other1="睡眠の確保1日7時間", other2="毎日の歩数の測定"),
                Template(main_disease="高血圧症", sheet_name="3_血圧140-90以下_歩行",
                         goal1="家庭血圧が測定でき、朝と就寝前のいずれかで140/90mmHg以下",
                         goal2="塩分を控えた食事と運動習慣を目標にする",
                         target_bp="140/90",
                         target_hba1c="",
                         diet1="塩分量を適正にする",
                         diet2="食物繊維の摂取量を増やす",
                         diet3="ゆっくり食べる",
                         diet4="間食を減らす",
                         exercise_prescription="ウォーキング", exercise_time="30分",
                         exercise_frequency="週に2日",
                         exercise_intensity="少し汗をかく程度", daily_activity="6000歩",
                         other1="睡眠の確保1日7時間", other2="毎日の歩数の測定"),
                Template(main_disease="脂質異常症", sheet_name="1_LDL120以下", goal1="LDLコレステロール＜120/TG＜150/HDL≧40",
                         goal2="毎日の有酸素運動と食習慣の改善",
                         target_bp="",
                         target_hba1c="",
                         diet1="食事量を適正にする",
                         diet2="食物繊維の摂取量を増やす",
                         diet3="ゆっくり食べる",
                         diet4="間食を減らす",
                         exercise_prescription="ウォーキング", exercise_time="30分",
                         exercise_frequency="週に2日",
                         exercise_intensity="少し汗をかく程度", daily_activity="5000歩",
                         other1="飲酒の制限、肥満度の改善", other2="毎日の歩数の測定"),
                Template(main_disease="脂質異常症", sheet_name="2_LDL100以下", goal1="LDLコレステロール＜100/TG＜150/HDL≧40",
                         goal2="毎日の有酸素運動と食習慣の改善",
                         target_bp="",
                         target_hba1c="",
                         diet1="食事量を適正にする",
                         diet2="食物繊維の摂取量を増やす",
                         diet3="ゆっくり食べる",
                         diet4="間食を減らす",
                         exercise_prescription="ウォーキング", exercise_time="30分",
                         exercise_frequency="週に2日",
                         exercise_intensity="少し汗をかく程度", daily_activity="5000歩",
                         other1="飲酒の制限、肥満度の改善", other2="毎日の歩数の測定"),
                Template(main_disease="脂質異常症", sheet_name="3_LDL70以下", goal1="LDLコレステロール＜100/TG＜150/HDL>40",
                         goal2="毎日の有酸素運動と食習慣の改善",
                         target_bp="",
                         target_hba1c="",
                         diet1="脂肪の多い食品や甘い物を控える",
                         diet2="食物繊維の摂取量を増やす",
                         diet3="ゆっくり食べる",
                         diet4="間食を減らす",
                         exercise_prescription="ウォーキング", exercise_time="30分",
                         exercise_frequency="週に2日",
                         exercise_intensity="少し汗をかく程度", daily_activity="5000歩",
                         other1="飲酒の制限、肥満度の改善", other2="毎日の歩数の測定"),
                Template(main_disease="糖尿病", sheet_name="1_HbA1c７％", goal1="HbA1ｃ７％/体重を当初の－３Kgとする",
                         goal2="5000歩の歩行/間食の制限/糖質の制限",
                         target_bp="130/80",
                         target_hba1c="7",
                         diet1="食事量を適正にする",
                         diet2="食物繊維の摂取量を増やす",
                         diet3="ゆっくり食べる",
                         diet4="間食を減らす",
                         exercise_prescription="ウォーキング", exercise_time="30分",
                         exercise_frequency="週に5日",
                         exercise_intensity="少し汗をかく程度", daily_activity="5000歩",
                         other1="睡眠の確保1日7時間", other2="毎日の歩数の測定"),
                Template(main_disease="糖尿病", sheet_name="2_HbA1c６％", goal1="HbA1ｃを正常化/HbA1ｃ6％",
                         goal2="1日5000歩以上の歩行/間食の制限/糖質の制限",
                         target_bp="130/80",
                         target_hba1c="6",
                         diet1="食事量を適正にする",
                         diet2="食物繊維の摂取量を増やす",
                         diet3="ゆっくり食べる",
                         diet4="間食を減らす",
                         exercise_prescription="ウォーキング", exercise_time="30分",
                         exercise_frequency="週に5日",
                         exercise_intensity="少し汗をかく程度", daily_activity="5000歩",
                         other1="睡眠の確保1日7時間", other2="毎日の歩数の測定"),
                Template(main_disease="糖尿病", sheet_name="3_HbA1c８％", goal1="HbA1ｃを低血糖に注意して下げる",
                         goal2="ストレッチを中心とした運動/間食の制限/糖質の制限",
                         target_bp="140/90",
                         target_hba1c="8",
                         diet1="食事量を適正にする",
                         diet2="食物繊維の摂取量を増やす",
                         diet3="ゆっくり食べる",
                         diet4="間食を減らす",
                         exercise_prescription="ストレッチ体操", exercise_time="10分",
                         exercise_frequency="週に2日",
                         exercise_intensity="息切れしない程度", daily_activity="ストレッチ運動を主に行う",
                         other1="睡眠の確保1日7時間", other2="家庭での血圧の測定"),
            ]
            session.add_all(templates)
            session.commit()
    finally:
        session.close()
