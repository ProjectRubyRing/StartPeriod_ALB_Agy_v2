# -*- coding: utf-8 -*-
"""
Script to generate ECS_Fargate_HealthCheck_GracePeriod_Guide.xlsx
Meiryo UI font, monotone-based styling, comprehensive architecture & parameter guide.
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_excel_guide(filename="ECS_Fargate_HealthCheck_GracePeriod_Guide.xlsx"):
    wb = openpyxl.Workbook()
    
    # -------------------------------------------------------------
    # Palette & Styles (Monotone Base)
    # -------------------------------------------------------------
    FONT_FAMILY = "Meiryo UI"
    
    font_title = Font(name=FONT_FAMILY, size=15, bold=True, color="FFFFFF")
    font_section = Font(name=FONT_FAMILY, size=11, bold=True, color="1F2937")
    font_header = Font(name=FONT_FAMILY, size=9.5, bold=True, color="FFFFFF")
    font_bold = Font(name=FONT_FAMILY, size=9, bold=True, color="111827")
    font_normal = Font(name=FONT_FAMILY, size=9, bold=False, color="1F2937")
    font_small = Font(name=FONT_FAMILY, size=8, bold=False, color="4B5563")
    font_code = Font(name=FONT_FAMILY, size=8.5, bold=False, color="111827")
    font_badge = Font(name=FONT_FAMILY, size=8.5, bold=True, color="FFFFFF")

    fill_title = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid") # Slate dark 900
    fill_header = PatternFill(start_color="334155", end_color="334155", fill_type="solid") # Slate 700
    fill_sub_header = PatternFill(start_color="475569", end_color="475569", fill_type="solid") # Slate 600
    fill_section = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid") # Slate 100
    fill_zebra_0 = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    fill_zebra_1 = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid") # Slate 50
    fill_note = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_badge_dark = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
    fill_highlight = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")

    thin_border_side = Side(border_style="thin", color="CBD5E1")
    border_all = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    border_top_thick = Border(top=Side(border_style="medium", color="475569"), bottom=thin_border_side, left=thin_border_side, right=thin_border_side)

    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)
    align_title = Alignment(horizontal="left", vertical="center", indent=1)

    # -------------------------------------------------------------
    # Helper Functions
    # -------------------------------------------------------------
    def apply_row_style(ws, row_idx, start_col, end_col, font=font_normal, fill=None, alignment=align_left, border=border_all):
        for col_idx in range(start_col, end_col + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            if font: cell.font = font
            if fill: cell.fill = fill
            if alignment: cell.alignment = alignment
            if border: cell.border = border

    def create_title_block(ws, title_text, subtitle_text, max_col=10):
        ws.merge_cells(start_row=2, start_column=2, end_row=2, end_column=max_col)
        cell = ws.cell(row=2, column=2, value=title_text)
        cell.font = font_title
        cell.fill = fill_title
        cell.alignment = align_title
        ws.row_dimensions[2].height = 36

        ws.merge_cells(start_row=3, start_column=2, end_row=3, end_column=max_col)
        cell_sub = ws.cell(row=3, column=2, value=subtitle_text)
        cell_sub.font = font_small
        cell_sub.fill = fill_section
        cell_sub.alignment = align_left
        ws.row_dimensions[3].height = 20
        apply_row_style(ws, 3, 2, max_col, font=font_small, fill=fill_section, alignment=align_left, border=border_all)

    # =============================================================
    # Sheet 1: エグゼクティブサマリ・比較
    # =============================================================
    ws1 = wb.active
    ws1.title = "1_エグゼクティブサマリ"
    ws1.views.sheetView[0].showGridLines = True
    create_title_block(ws1, "AWS ECS Fargate ヘルスチェック & ALB Grace Period 設計ガイド", 
                       "概要・課題分析・3つのアーキテクチャパターンの比較と推奨構成（モノトーン仕様 / Meiryo UI）", max_col=8)

    # Section 1: 課題の要約
    ws1.cell(row=5, column=2, value="【1】 現状の課題と300秒タイムアウト障害の発生メカニズム").font = font_section
    ws1.merge_cells(start_row=5, start_column=2, end_row=5, end_column=8)
    apply_row_style(ws1, 5, 2, 8, font=font_section, fill=fill_section, alignment=align_left, border=border_all)
    ws1.row_dimensions[5].height = 25

    problem_desc = (
        "■ 課題の根本原因：\n"
        "タスク定義で「フロントコンテナ depends_on バックコンテナ (Condition: HEALTHY)」と直列依存を設定した場合、\n"
        "① ADOT Collector起動＆HEALTHY化 (~10秒) → ② バックコンテナ起動＆JBossデプロイ完了＆HEALTHY化 (最大160秒) が完了するまで、\n"
        "フロントコンテナの起動プロセスそのものがECSによって保留（ブロック）されます。\n"
        "バックコンテナがHEALTHYになった時点（約170秒経過）でフロントコンテナがようやく起動を開始しますが、フロントの起動にも最大140秒かかります。\n"
        "結果として「全体の準備完了時間 = 10秒 + 160秒 + 140秒 = 310秒」となり、ALBのGrace Period (300秒) を超過します。\n"
        "300秒経過時点でALBは「フロントがまだ応答しない（起動中）」と判定してタスクを異常とみなし、強制停止・再作成の無限ループ（CrashLoop）に陥ります。"
    )
    ws1.merge_cells(start_row=6, start_column=2, end_row=6, end_column=8)
    cell_p = ws1.cell(row=6, column=2, value=problem_desc)
    cell_p.font = font_normal
    cell_p.alignment = align_left
    cell_p.fill = fill_zebra_1
    apply_row_style(ws1, 6, 2, 8, font=font_normal, fill=fill_zebra_1, alignment=align_left, border=border_all)
    ws1.row_dimensions[6].height = 95

    # Section 2: 3つのパターン比較
    ws1.cell(row=8, column=2, value="【2】 解決策のパターン比較（直列・並列・ハイブリッド）").font = font_section
    ws1.merge_cells(start_row=8, start_column=2, end_row=8, end_column=8)
    apply_row_style(ws1, 8, 2, 8, font=font_section, fill=fill_section, alignment=align_left, border=border_all)
    ws1.row_dimensions[8].height = 25

    headers_pattern = ["パターン名", "依存関係構成 (depends_on)", "コンテナ起動方式", "タスク準備完了時間", "ALB Grace Period設定値", "メリット", "デメリット・リスク"]
    for i, h in enumerate(headers_pattern):
        c = ws1.cell(row=9, column=i+2, value=h)
        c.font = font_header
        c.fill = fill_header
        c.alignment = align_center
        c.border = border_all
    ws1.row_dimensions[9].height = 28

    patterns_data = [
        ("パターン1\n完全直列依存\n(安全重視・長時間)", 
         "ADOT: なし\nCW Agent: なし\nバック: ADOT (HEALTHY)\nフロント: バック (HEALTHY)", 
         "完全直列\nADOT → バック → フロント", 
         "約 310秒\n(10s + 160s + 140s)", 
         "420秒 (7分)\n※現在の300秒から延長必須", 
         "・フロント起動時にバックエンドAPIが100%確実に稼働している\n・フロント側の初期化エラーが原理的に発生しない\n・トレース欠損が完全にゼロ", 
         "・デプロイに7分以上かかり、ローリングアップデートが極めて遅い\n・オートスケーリングの追従性が著しく悪化する\n・ECS Grace Periodの延長が必要不可欠"),
        
        ("パターン2\n並列起動＋内部HC\n★【強く推奨】", 
         "ADOT: なし\nCW Agent: なし\nバック: ADOT (HEALTHY)\nフロント: ADOT (HEALTHY)\n※フロント-バック間の依存解除", 
         "並列起動\nバックとフロントが\n同時にJBoss起動開始", 
         "約 165秒\n(10s + MAX(160s, 140s))", 
         "300秒 (現状のまま維持可能)\n(余裕時間: 約135秒)", 
         "・タスク起動時間が310秒から165秒へほぼ半減\n・現行のALB Grace Period (300秒) を変更せず安全に収まる\n・フロントのヘルスチェックでバック疎通を確認するため安全性も担保", 
         "・フロントのSpring起動時にバック疎通を前提としたEagerなBean初期化があるとエラーになる（Lazy初期化や再試行が必要）\n・起動時に2つのJBossが同時にCPUを使用するためリソース割当に配慮が必要"),
        
        ("パターン3\nハイブリッド依存\n(START条件)", 
         "ADOT: なし\nCW Agent: なし\nバック: ADOT (HEALTHY)\nフロント: バック (START)", 
         "準並列起動\nバックのプロセス生成直後に\nフロントが起動開始", 
         "約 170秒\n(10s + 2s + 160s)", 
         "300秒 (現状維持可能)\n(余裕時間: 約130秒)", 
         "・バックエンドのコンテナプロセスが確実に立ち上がってからフロントが起動する\n・コンテナの起動順序は保ちつつ、直列デプロイ待機時間を解消できる", 
         "・パターン2と同様に、バックエンドのJBoss/Springが完全起動する前にフロントが起動するため、フロント側の耐障害性設計が必要"),
        
        ("パターン4\n(参考・将来像)\nタスク完全分離構成", 
         "フロントエンドタスクと\nバックエンドタスクを別々の\nECSサービスに分離", 
         "独立起動\nService Connect または\n内部ALB経由で通信", 
         "各タスク独立\n(バック160s / フロント140s)", 
         "バック: 240秒\nフロント: 210秒", 
         "・コンテナ間の起動依存関係が完全に解消される\n・スケールアウトがフロント/バック個別に最適化できる\n・AWS Well-Architectedの推奨ベストプラクティス", 
         "・タスク定義の分割、Service Connect/内部ALBの追加構築が必要となり、現在の単一タスク構成からアーキテクチャ変更が必要")
    ]

    for r_idx, p in enumerate(patterns_data, start=10):
        fill_curr = fill_highlight if r_idx == 11 else (fill_zebra_0 if r_idx % 2 == 0 else fill_zebra_1)
        ws1.row_dimensions[r_idx].height = 80
        for c_idx, val in enumerate(p):
            cell = ws1.cell(row=r_idx, column=c_idx+2, value=val)
            cell.font = font_bold if (c_idx == 0 or r_idx == 11) else font_normal
            cell.fill = fill_curr
            cell.alignment = align_center if c_idx in [0, 2, 3, 4] else align_left
            cell.border = border_all

    # Section 3: 結論と推奨アクション
    ws1.cell(row=15, column=2, value="【3】 結論と採用すべき推奨設計").font = font_section
    ws1.merge_cells(start_row=15, start_column=2, end_row=15, end_column=8)
    apply_row_style(ws1, 15, 2, 8, font=font_section, fill=fill_section, alignment=align_left, border=border_all)
    ws1.row_dimensions[15].height = 25

    conclusion_desc = (
        "1. 直列化の回避（パターン2の採用を強く推奨）：\n"
        "   フロントコンテナのコンテナヘルスチェックが内部で『https://localhost:18080/iwinmichl/healthcheck』を呼び出して200を確認しているため、\n"
        "   フロントとバック間の depends_on を解除して並列起動させても、バックエンドが準備完了するまでフロントコンテナは HEALTHY になりません。\n"
        "   これにより、ALBからトラフィックが流し込まれる前に両方のコンテナが完全に立ち上がっている状態を確実に保証できます。\n\n"
        "2. ALB Grace Period の設定：\n"
        "   パターン2を採用する場合、最大起動時間は約165秒となるため、現在の『300秒』の設定値で十分な安全マージン（約135秒のバッファ）が確保されます。\n"
        "   一方、業務上の制約等でどうしても直列依存（パターン1）を維持しなければならない場合は、Grace Period を直ちに『420秒（7分）』に延長してください。"
    )
    ws1.merge_cells(start_row=16, start_column=2, end_row=16, end_column=8)
    cell_c = ws1.cell(row=16, column=2, value=conclusion_desc)
    cell_c.font = font_normal
    cell_c.alignment = align_left
    cell_c.fill = fill_zebra_0
    apply_row_style(ws1, 16, 2, 8, font=font_normal, fill=fill_zebra_0, alignment=align_left, border=border_all)
    ws1.row_dimensions[16].height = 95


    # =============================================================
    # Sheet 2: 設定値一覧_パターン別
    # =============================================================
    ws2 = wb.create_sheet(title="2_設定値一覧_パターン別")
    ws2.views.sheetView[0].showGridLines = True
    create_title_block(ws2, "コンテナヘルスチェック & ALB Grace Period 詳細パラメータ設計一覧", 
                       "4つのコンテナ（ADOT, CW Agent, バック, フロント）およびALBターゲットグループの完全設定マトリクス", max_col=10)

    # 3つのパターンの詳細パラメータブロック
    sheet2_patterns = [
        ("【パターン1】 完全直列依存構成（安全重視・ALB Grace Period 420秒へ延長）", 420, [
            ("ADOT Collector", "true", "なし（即時起動）", "-", "CMD", "curl -f http://localhost:13133/ || exit 1", 5, 3, 2, 10, "Go言語バイナリ。数秒で起動完了。バックのトレース受信用"),
            ("CloudWatch Agent", "true", "なし（即時起動）", "-", "CMD-SHELL", "/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -m ec2 -a status | grep running || exit 1", 10, 5, 2, 15, "メトリクス収集用エージェント。他コンテナとの起動依存なし"),
            ("バックエンドコンテナ", "true", "adot-collector", "HEALTHY", "CMD-SHELL", "curl -k -f https://localhost:18080/iwinmichl/healthcheck || exit 1", 10, 5, 3, 160, "ADOT準備完了後にJBoss起動。実測20-80s+バッファ80s=160s"),
            ("フロントエンドコンテナ", "true", "backend-container", "HEALTHY", "CMD-SHELL", "curl -k -f https://localhost:18080/iwinmichl/healthcheck || exit 1", 10, 5, 3, 140, "バックのHEALTHYを待ってからJBoss起動。実測15-70s+バッファ70s=140s")
        ]),
        ("【パターン2】 並列起動構成 ★【推奨】（フロント-バック依存解除・ALB Grace Period 300秒維持）", 300, [
            ("ADOT Collector", "true", "なし（即時起動）", "-", "CMD", "curl -f http://localhost:13133/ || exit 1", 5, 3, 2, 10, "Go言語バイナリ。即時起動し13133ポートでヘルスチェックOKを返す"),
            ("CloudWatch Agent", "true", "なし（即時起動）", "-", "CMD-SHELL", "/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -m ec2 -a status | grep running || exit 1", 10, 5, 2, 15, "プロセス生存確認。他コンテナと並列起動"),
            ("バックエンドコンテナ", "true", "adot-collector", "HEALTHY", "CMD-SHELL", "curl -k -f https://localhost:18080/iwinmichl/healthcheck || exit 1", 10, 5, 3, 160, "ADOTのHEALTHY到達後にJBoss起動。トレース完全保持"),
            ("フロントエンドコンテナ", "true", "adot-collector", "HEALTHY", "CMD-SHELL", "curl -k -f https://localhost:18080/iwinmichl/healthcheck || exit 1", 10, 5, 3, 160, "バックと並行してJBoss起動。内部HCでバックの準備完了を待つ(160s)")
        ]),
        ("【パターン3】 ハイブリッド依存構成（depends_on: START・ALB Grace Period 300秒維持）", 300, [
            ("ADOT Collector", "true", "なし（即時起動）", "-", "CMD", "curl -f http://localhost:13133/ || exit 1", 5, 3, 2, 10, "即時起動"),
            ("CloudWatch Agent", "true", "なし（即時起動）", "-", "CMD-SHELL", "/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -m ec2 -a status | grep running || exit 1", 10, 5, 2, 15, "並列起動"),
            ("バックエンドコンテナ", "true", "adot-collector", "HEALTHY", "CMD-SHELL", "curl -k -f https://localhost:18080/iwinmichl/healthcheck || exit 1", 10, 5, 3, 160, "ADOTのHEALTHY到達後に起動開始"),
            ("フロントエンドコンテナ", "true", "backend-container", "START", "CMD-SHELL", "curl -k -f https://localhost:18080/iwinmichl/healthcheck || exit 1", 10, 5, 3, 160, "バックのコンテナ作成直後にフロント起動開始。内部HCでバック完了待ち")
        ])
    ]

    curr_row = 5
    for p_title, alb_gp, c_list in sheet2_patterns:
        ws2.cell(row=curr_row, column=2, value=p_title).font = font_section
        ws2.merge_cells(start_row=curr_row, start_column=2, end_row=curr_row, end_column=10)
        apply_row_style(ws2, curr_row, 2, 10, font=font_section, fill=fill_section, alignment=align_left, border=border_all)
        ws2.row_dimensions[curr_row].height = 24
        curr_row += 1

        headers_c = ["コンテナ名", "essential", "depends_on 対象", "Condition", "Command Type", "HealthCheck コマンド", "Interval (s)", "Timeout (s)", "Retries", "startPeriod (s)"]
        for ci, ch in enumerate(headers_c):
            c = ws2.cell(row=curr_row, column=ci+1, value=ch)
            c.font = font_header
            c.fill = fill_sub_header
            c.alignment = align_center
            c.border = border_all
        ws2.row_dimensions[curr_row].height = 25
        curr_row += 1

        for c_data in c_list:
            ws2.row_dimensions[curr_row].height = 28
            vals = [c_data[0], c_data[1], c_data[2], c_data[3], c_data[4], c_data[5], c_data[6], c_data[7], c_data[8], c_data[9]]
            for c_idx, val in enumerate(vals):
                cell = ws2.cell(row=curr_row, column=c_idx+1, value=val)
                cell.font = font_code if c_idx == 5 else font_normal
                cell.fill = fill_zebra_0 if curr_row % 2 == 0 else fill_zebra_1
                cell.alignment = align_left if c_idx in [0, 5] else align_center
                cell.border = border_all
            curr_row += 1

        # ALB設定まとめ行
        alb_summary_text = (
            f"★ ALB & ECSサービス設定値 ── healthCheckGracePeriodSeconds: {alb_gp}秒 | "
            f"Target Group HealthCheck Path: /health (または業務HCパス) | Interval: 15秒 | Timeout: 5秒 | HealthyThreshold: 2回 | UnhealthyThreshold: 3回"
        )
        ws2.merge_cells(start_row=curr_row, start_column=1, end_row=curr_row, end_column=10)
        c_alb = ws2.cell(row=curr_row, column=1, value=alb_summary_text)
        c_alb.font = font_bold
        c_alb.fill = fill_highlight
        c_alb.alignment = align_left
        apply_row_style(ws2, curr_row, 1, 10, font=font_bold, fill=fill_highlight, alignment=align_left, border=border_all)
        ws2.row_dimensions[curr_row].height = 25
        curr_row += 2  # 空白行を挟む

    # パラメータ範囲とデフォルト値の注釈テーブル
    ws2.cell(row=curr_row, column=1, value="【各パラメータの仕様・設定可能範囲・デフォルト値】").font = font_section
    ws2.merge_cells(start_row=curr_row, start_column=1, end_row=curr_row, end_column=10)
    apply_row_style(ws2, curr_row, 1, 10, font=font_section, fill=fill_section, alignment=align_left, border=border_all)
    ws2.row_dimensions[curr_row].height = 24
    curr_row += 1

    param_specs = [
        ("startPeriod", "0 〜 300 秒 (ECS仕様)", "0 秒", "コンテナ起動直後にヘルスチェックが失敗してもリトライ上限(retries)にカウントしない猶予期間。一度成功するとその瞬間に終了しHEALTHYとなる。"),
        ("interval", "5 〜 300 秒", "30 秒", "ヘルスチェックプローブを実行する間隔。短すぎるとCPU負荷になり、長すぎると復旧検知が遅れる。10秒が推奨値。"),
        ("timeout", "2 〜 60 秒", "5 秒", "プローブコマンドの応答タイムアウト。intervalより小さく設定する必要がある。通常2〜5秒で十分。"),
        ("retries", "1 〜 10 回", "3 回", "連続して失敗した場合にUNHEALTHYと判定する回数。一時的な瞬断を防ぐため通常2〜3回を設定する。"),
        ("depends_on Condition", "START, COMPLETE, SUCCESS, HEALTHY", "なし", "HEALTHYを指定した場合、対象コンテナが自身のヘルスチェックに合格するまで起動がブロックされる。"),
        ("ALB Grace Period", "0 〜 2147483647 秒", "0 秒 (デフォルトなし)", "タスク起動からこの秒数が経過するまで、ALBターゲットのヘルスチェック失敗によるタスク強制終了を抑止する。")
    ]
    headers_spec = ["設定パラメータ", "有効範囲・設定可能値", "AWSデフォルト値", "動作内容および推奨設定の根拠"]
    ws2.merge_cells(start_row=curr_row, start_column=1, end_row=curr_row, end_column=2)
    ws2.cell(row=curr_row, column=1, value=headers_spec[0]).font = font_header
    ws2.cell(row=curr_row, column=1).fill = fill_sub_header
    ws2.cell(row=curr_row, column=1).alignment = align_center
    ws2.cell(row=curr_row, column=1).border = border_all
    ws2.cell(row=curr_row, column=2).border = border_all
    ws2.cell(row=curr_row, column=2).fill = fill_sub_header

    ws2.merge_cells(start_row=curr_row, start_column=3, end_row=curr_row, end_column=4)
    ws2.cell(row=curr_row, column=3, value=headers_spec[1]).font = font_header
    ws2.cell(row=curr_row, column=3).fill = fill_sub_header
    ws2.cell(row=curr_row, column=3).alignment = align_center
    ws2.cell(row=curr_row, column=3).border = border_all
    ws2.cell(row=curr_row, column=4).border = border_all
    ws2.cell(row=curr_row, column=4).fill = fill_sub_header

    ws2.merge_cells(start_row=curr_row, start_column=5, end_row=curr_row, end_column=6)
    ws2.cell(row=curr_row, column=5, value=headers_spec[2]).font = font_header
    ws2.cell(row=curr_row, column=5).fill = fill_sub_header
    ws2.cell(row=curr_row, column=5).alignment = align_center
    ws2.cell(row=curr_row, column=5).border = border_all
    ws2.cell(row=curr_row, column=6).border = border_all
    ws2.cell(row=curr_row, column=6).fill = fill_sub_header

    ws2.merge_cells(start_row=curr_row, start_column=7, end_row=curr_row, end_column=10)
    ws2.cell(row=curr_row, column=7, value=headers_spec[3]).font = font_header
    ws2.cell(row=curr_row, column=7).fill = fill_sub_header
    ws2.cell(row=curr_row, column=7).alignment = align_center
    apply_row_style(ws2, curr_row, 7, 10, font=font_header, fill=fill_sub_header, alignment=align_center, border=border_all)
    ws2.row_dimensions[curr_row].height = 24
    curr_row += 1

    for ps in param_specs:
        ws2.merge_cells(start_row=curr_row, start_column=1, end_row=curr_row, end_column=2)
        ws2.cell(row=curr_row, column=1, value=ps[0]).font = font_bold
        ws2.cell(row=curr_row, column=1).alignment = align_left
        ws2.cell(row=curr_row, column=1).fill = fill_zebra_0 if curr_row % 2 == 0 else fill_zebra_1
        apply_row_style(ws2, curr_row, 1, 2, font=font_bold, fill=(fill_zebra_0 if curr_row % 2 == 0 else fill_zebra_1), alignment=align_left, border=border_all)

        ws2.merge_cells(start_row=curr_row, start_column=3, end_row=curr_row, end_column=4)
        ws2.cell(row=curr_row, column=3, value=ps[1]).font = font_normal
        ws2.cell(row=curr_row, column=3).alignment = align_center
        apply_row_style(ws2, curr_row, 3, 4, font=font_normal, fill=(fill_zebra_0 if curr_row % 2 == 0 else fill_zebra_1), alignment=align_center, border=border_all)

        ws2.merge_cells(start_row=curr_row, start_column=5, end_row=curr_row, end_column=6)
        ws2.cell(row=curr_row, column=5, value=ps[2]).font = font_normal
        ws2.cell(row=curr_row, column=5).alignment = align_center
        apply_row_style(ws2, curr_row, 5, 6, font=font_normal, fill=(fill_zebra_0 if curr_row % 2 == 0 else fill_zebra_1), alignment=align_center, border=border_all)

        ws2.merge_cells(start_row=curr_row, start_column=7, end_row=curr_row, end_column=10)
        ws2.cell(row=curr_row, column=7, value=ps[3]).font = font_normal
        ws2.cell(row=curr_row, column=7).alignment = align_left
        apply_row_style(ws2, curr_row, 7, 10, font=font_normal, fill=(fill_zebra_0 if curr_row % 2 == 0 else fill_zebra_1), alignment=align_left, border=border_all)
        ws2.row_dimensions[curr_row].height = 36
        curr_row += 1


    # =============================================================
    # Sheet 3: デプロイバッファ内訳計算
    # =============================================================
    ws3 = wb.create_sheet(title="3_デプロイバッファ内訳計算")
    ws3.views.sheetView[0].showGridLines = True
    create_title_block(ws3, "JBoss EAP デプロイ時間実測値分析とデプロイバッファ内訳計算", 
                       "実測時間の揺れ要因・バッファ算出根拠・秒数内訳・210秒設定との整合性検証", max_col=8)

    ws3.cell(row=5, column=2, value="【1】 コンテナ別 デプロイ時間実測値と基本算出式").font = font_section
    ws3.merge_cells(start_row=5, start_column=2, end_row=5, end_column=8)
    apply_row_style(ws3, 5, 2, 8, font=font_section, fill=fill_section, alignment=align_left, border=border_all)
    ws3.row_dimensions[5].height = 25

    headers_buffer = ["対象コンテナ", "実測最小時間", "実測最大時間", "実測の揺れ幅", "算出方式 (見積もり基準)", "デプロイバッファ秒数", "最終設定startPeriod"]
    for i, h in enumerate(headers_buffer):
        c = ws3.cell(row=6, column=i+2, value=h)
        c.font = font_header
        c.fill = fill_header
        c.alignment = align_center
        c.border = border_all
    ws3.row_dimensions[6].height = 26

    calc_rows = [
        ("バックエンドコンテナ (JBoss EAP)", "20 秒", "80 秒", "60 秒 (20〜80s)", "最大実測値 × 2.0 (100%バッファ)", "80 秒", "160 秒"),
        ("フロントエンドコンテナ (JBoss EAP)", "15 秒", "70 秒", "55 秒 (15〜70s)", "最大実測値 × 2.0 (100%バッファ)", "70 秒", "140 秒"),
        ("ADOT Collector (Goバイナリ)", "1 秒", "3 秒", "2 秒 (1〜3s)", "最大実測値 ＋ 安全余裕 7s", "7 秒", "10 秒"),
        ("CloudWatch Agent (Goバイナリ)", "2 秒", "5 秒", "3 秒 (2〜5s)", "最大実測値 ＋ 安全余裕 10s", "10 秒", "15 秒")
    ]
    for r_idx, cr in enumerate(calc_rows, start=7):
        ws3.row_dimensions[r_idx].height = 24
        for c_idx, val in enumerate(cr):
            cell = ws3.cell(row=r_idx, column=c_idx+2, value=val)
            cell.font = font_bold if c_idx in [0, 6] else font_normal
            cell.fill = fill_zebra_0 if r_idx % 2 == 1 else fill_zebra_1
            cell.alignment = align_left if c_idx == 0 else align_center
            cell.border = border_all

    # Section 2: デプロイバッファの内訳詳細
    ws3.cell(row=12, column=2, value="【2】 デプロイバッファに含まれる時間の詳細内訳（なぜ最大実測値と同等のバッファが必要か）").font = font_section
    ws3.merge_cells(start_row=12, start_column=2, end_row=12, end_column=8)
    apply_row_style(ws3, 12, 2, 8, font=font_section, fill=fill_section, alignment=align_left, border=border_all)
    ws3.row_dimensions[12].height = 25

    headers_items = ["内訳項目（遅延・揺れの要因）", "バックエンド加算時間", "フロントエンド加算時間", "発生メカニズムと詳細理由 (JBoss EAP / Fargate / Spring 特性)"]
    ws3.cell(row=13, column=2, value=headers_items[0]).font = font_header
    ws3.cell(row=13, column=2).fill = fill_sub_header
    ws3.cell(row=13, column=2).alignment = align_center
    ws3.cell(row=13, column=2).border = border_all

    ws3.cell(row=13, column=3, value=headers_items[1]).font = font_header
    ws3.cell(row=13, column=3).fill = fill_sub_header
    ws3.cell(row=13, column=3).alignment = align_center
    ws3.cell(row=13, column=3).border = border_all

    ws3.cell(row=13, column=4, value=headers_items[2]).font = font_header
    ws3.cell(row=13, column=4).fill = fill_sub_header
    ws3.cell(row=13, column=4).alignment = align_center
    ws3.cell(row=13, column=4).border = border_all

    ws3.merge_cells(start_row=13, start_column=5, end_row=13, end_column=8)
    ws3.cell(row=13, column=5, value=headers_items[3]).font = font_header
    ws3.cell(row=13, column=5).fill = fill_sub_header
    ws3.cell(row=13, column=5).alignment = align_center
    apply_row_style(ws3, 13, 5, 8, font=font_header, fill=fill_sub_header, alignment=align_center, border=border_all)
    ws3.row_dimensions[13].height = 25

    buffer_breakdown_data = [
        ("① Fargate vCPU スロットリング・共有リソース競合バッファ", "＋25 秒", "＋20 秒",
         "Fargateタスク割り当てvCPU上で、複数コンテナ（ADOT, JBoss×2台）が同時に起動するとCPU使用率が100%に張り付きます。CFS（Completely Fair Scheduler）による時分割スロットリングが発生し、単体起動時よりもスレッド実行が遅延します。"),
        
        ("② DBコネクションプール確立＆SSLハンドシェイク遅延バッファ", "＋20 秒", "＋5 秒 (間接影響)",
         "JBoss起動時、IronJacamar / HikariCPがAmazon Aurora RDS等のデータベースに対して初期接続プール（Initial Pool Size）を一括確立します。DNS名前解決・TLS/SSL鍵交換・認証・ネットワークRTTの揺れにより最大20秒の揺れが生じます。"),
        
        ("③ JVM JITコンパイル＆G1GC一時停止（STW）バッファ", "＋15 秒", "＋15 秒",
         "JBoss Modulesによる数千クラスのロード時、JVMヒープへのオブジェクト急増に伴いG1GCのYoung GCが連続発生します。またC2 JITコンパイラが起動時バイトコードをネイティブコンパイルする際のCPU負荷で一時的なStop-The-Worldが発生します。"),
        
        ("④ Spring Context 初期化＆リトライ待機バッファ", "＋0 秒 (自己完結)", "＋15 秒",
         "フロントエンド起動時、Spring Bean定義のスキャン、HandlerMapping登録、内部RESTクライアント生成が行われます。バックエンドへの初回疎通が一時的に接続拒否(ECONNREFUSED)となった際のバックオフ待機時間を吸収します。"),
        
        ("⑤ ヘルスチェック周期（Interval）およびサンプリング遅れバッファ", "＋20 秒 (Interval 10s×2回)", "＋15 秒 (Interval 10s＋α)",
         "JBossのデプロイが完了した瞬間（80秒時点）と、ECSエージェントがヘルスチェックコマンドを実行するタイミングには周期的なズレ（最大10秒）があります。さらにコマンド実行時間(2〜3秒)や連続成功判定の周期ズレを吸収するために必須となります。")
    ]

    for b_idx, b_item in enumerate(buffer_breakdown_data, start=14):
        ws3.row_dimensions[b_idx].height = 45
        ws3.cell(row=b_idx, column=2, value=b_item[0]).font = font_bold
        ws3.cell(row=b_idx, column=2).fill = fill_zebra_0 if b_idx % 2 == 0 else fill_zebra_1
        ws3.cell(row=b_idx, column=2).alignment = align_left
        ws3.cell(row=b_idx, column=2).border = border_all

        ws3.cell(row=b_idx, column=3, value=b_item[1]).font = font_normal
        ws3.cell(row=b_idx, column=3).fill = fill_zebra_0 if b_idx % 2 == 0 else fill_zebra_1
        ws3.cell(row=b_idx, column=3).alignment = align_center
        ws3.cell(row=b_idx, column=3).border = border_all

        ws3.cell(row=b_idx, column=4, value=b_item[2]).font = font_normal
        ws3.cell(row=b_idx, column=4).fill = fill_zebra_0 if b_idx % 2 == 0 else fill_zebra_1
        ws3.cell(row=b_idx, column=4).alignment = align_center
        ws3.cell(row=b_idx, column=4).border = border_all

        ws3.merge_cells(start_row=b_idx, start_column=5, end_row=b_idx, end_column=8)
        ws3.cell(row=b_idx, column=5, value=b_item[3]).font = font_normal
        ws3.cell(row=b_idx, column=5).fill = fill_zebra_0 if b_idx % 2 == 0 else fill_zebra_1
        ws3.cell(row=b_idx, column=5).alignment = align_left
        apply_row_style(ws3, b_idx, 5, 8, font=font_normal, fill=(fill_zebra_0 if b_idx % 2 == 0 else fill_zebra_1), alignment=align_left, border=border_all)

    # 合計行
    ws3.cell(row=19, column=2, value="バッファ合計秒数（最大実測値に加算）").font = font_bold
    ws3.cell(row=19, column=2).fill = fill_highlight
    ws3.cell(row=19, column=2).alignment = align_left
    ws3.cell(row=19, column=2).border = border_all

    ws3.cell(row=19, column=3, value="80 秒 (＝実測最大 80s)").font = font_bold
    ws3.cell(row=19, column=3).fill = fill_highlight
    ws3.cell(row=19, column=3).alignment = align_center
    ws3.cell(row=19, column=3).border = border_all

    ws3.cell(row=19, column=4, value="70 秒 (＝実測最大 70s)").font = font_bold
    ws3.cell(row=19, column=4).fill = fill_highlight
    ws3.cell(row=19, column=4).alignment = align_center
    ws3.cell(row=19, column=4).border = border_all

    ws3.merge_cells(start_row=19, start_column=5, end_row=19, end_column=8)
    ws3.cell(row=19, column=5, value="合計startPeriod ── バックエンド: 80s＋80s＝160秒 ／ フロントエンド: 70s＋70s＝140秒").font = font_bold
    ws3.cell(row=19, column=5).fill = fill_highlight
    ws3.cell(row=19, column=5).alignment = align_left
    apply_row_style(ws3, 19, 5, 8, font=font_bold, fill=fill_highlight, alignment=align_left, border=border_all)
    ws3.row_dimensions[19].height = 25

    # 210秒設定の検証ブロック
    ws3.cell(row=21, column=2, value="【3】 当初検討されていた「startPeriod: 210秒」との比較検証").font = font_section
    ws3.merge_cells(start_row=21, start_column=2, end_row=21, end_column=8)
    apply_row_style(ws3, 21, 2, 8, font=font_section, fill=fill_section, alignment=align_left, border=border_all)
    ws3.row_dimensions[21].height = 25

    eval_210_text = (
        "■ なぜ210秒が検討されたのか？\n"
        "・フロント・バック両コンテナに一律で最大実測値の約3倍（70秒×3＝210秒、80秒×2.6倍＝208秒≒210秒）の極めて手厚い安全率を設定した運用想定値。\n\n"
        "■ 210秒設定の注意点と影響：\n"
        "① 直列構成（パターン1）で両方に210秒を設定した場合：\n"
        "   バックが最悪210秒、フロントが最悪210秒待機するため、合計起動猶予は『420秒超』となります。この場合、ALB Grace Period 300秒では確実に死亡します。\n"
        "② 並列構成（パターン2）で両方に210秒（または160秒）を設定した場合：\n"
        "   両コンテナは並行して起動するため、全体の待機時間は最大210秒で済みます。ALB Grace Period 300秒以内に余裕を持って収まるため、実害はありません。\n"
        "③ 結論：\n"
        "   コンテナごとの最適値（バック160秒、フロント140秒〜160秒）を設定するのが最も美しい設計ですが、運用簡素化のため一律210秒とする場合であっても、\n"
        "   『並列構成（パターン2）』であればALB Grace Period 300秒の範囲内で安全に動作します。"
    )
    ws3.merge_cells(start_row=22, start_column=2, end_row=22, end_column=8)
    cell_eval = ws3.cell(row=22, column=2, value=eval_210_text)
    cell_eval.font = font_normal
    cell_eval.alignment = align_left
    cell_eval.fill = fill_zebra_0
    apply_row_style(ws3, 22, 2, 8, font=font_normal, fill=fill_zebra_0, alignment=align_left, border=border_all)
    ws3.row_dimensions[22].height = 120


    # =============================================================
    # Sheet 4: 動作タイムライン比較
    # =============================================================
    ws4 = wb.create_sheet(title="4_動作タイムライン比較")
    ws4.views.sheetView[0].showGridLines = True
    create_title_block(ws4, "タスク起動からALBトラフィック導通までの時系列タイムラインシミュレーション", 
                       "障害発生シナリオ（パターン1×300s）と成功シナリオ（パターン2×300s / パターン1×420s）の秒単位推移", max_col=8)

    headers_tl = ["経過時間 (秒)", "ADOT Collector 状態", "CloudWatch Agent 状態", "バックエンドコンテナ 状態", "フロントエンドコンテナ 状態", "ALB Target Group 状態", "判定結果・イベント"]
    for i, h in enumerate(headers_tl):
        c = ws4.cell(row=5, column=i+2, value=h)
        c.font = font_header
        c.fill = fill_header
        c.alignment = align_center
        c.border = border_all
    ws4.row_dimensions[5].height = 26

    # タイムラインデータ: パターン1 (失敗), パターン2 (成功)
    timeline_events = [
        ("0秒", "タスク作成・起動開始", "タスク作成・起動開始", "待機中 (ADOTのHEALTHY待ち)", "待機中 (バックのHEALTHY待ち)", "Unhealthy (タスク登録・初期化中)", "ALB Grace Period タイマー開始(300s)"),
        ("5秒", "13133ポート疎通確認OK", "プロセス確認OK (Running)", "待機中 (ADOTのHC完了待ち)", "待機中 (バックのHEALTHY待ち)", "Unhealthy", "ADOT 初回ヘルスチェック成功"),
        ("10秒", "★ HEALTHY 到達", "★ HEALTHY 到達", "起動開始 (JBoss起動/クラスロード)", "待機中 (バックのHEALTHY待ち)", "Unhealthy", "バックエンドが依存条件満たし起動開始"),
        ("30秒", "稼働中 (トレース受信中)", "稼働中 (メトリクス収集)", "JBoss起動中 (データソース接続)", "待機中 (ブロック中)", "Unhealthy", "バックエンドがAuroraとプール接続"),
        ("80秒", "稼働中", "稼働中", "JBossデプロイ完了 (通常実測値)", "待機中 (ブロック中)", "Unhealthy", "バックエンドのSpringデプロイ完了"),
        ("90秒", "稼働中", "稼働中", "★ 通常時 HEALTHY 到達", "起動開始 (通常時)", "Unhealthy", "【通常ケース】フロントが起動開始"),
        ("160秒", "稼働中", "稼働中", "★ 最悪時 HEALTHY 到達", "起動開始 (最悪時)", "Unhealthy", "【最悪ケース】フロントが起動開始"),
        ("230秒", "稼働中", "稼働中", "稼働中 (HEALTHY)", "JBossデプロイ完了 (通常時)", "Unhealthy → Healthy チェック中", "【通常ケース】フロントがJBoss起動完了"),
        ("260秒", "稼働中", "稼働中", "稼働中 (HEALTHY)", "★ 通常時 HEALTHY 到達", "Healthy (2回連続成功)", "【通常ケース】ALB疎通OK (ギリギリ間に合う)"),
        ("300秒\n【運命の境界】", "稼働中", "稼働中", "稼働中 (HEALTHY)", "【最悪時】まだJBossデプロイ中！\n(160秒開始＋140秒必要＝300秒時点)", "Unhealthy\n(フロント未応答)", "★【障害発生】ALB Grace Period期限切れ！\nECSがタスクを強制停止・再作成へ"),
        ("310秒", "停止処理中", "停止処理中", "停止処理中", "【最悪時】本来ここでデプロイ完了", "Deregistering", "タスクが殺されたためデプロイ失敗"),
        ("───", "───", "───", "───", "───", "───", "─── パターン2（並列起動）の場合の推移 ───"),
        ("0秒", "起動開始", "起動開始", "待機中 (ADOT待ち)", "待機中 (ADOT待ち)", "Unhealthy", "ALB Grace Period タイマー開始(300s)"),
        ("10秒", "★ HEALTHY 到達", "★ HEALTHY 到達", "起動開始 (JBoss EAP)", "起動開始 (JBoss EAP 並列起動！)", "Unhealthy", "バックとフロントが同時に起動開始！"),
        ("90秒", "稼働中", "稼働中", "JBoss起動完了 (通常実測)", "JBoss起動完了 (通常実測)", "Unhealthy → Healthy チェック中", "両コンテナがデプロイ完了"),
        ("105秒", "稼働中", "稼働中", "★ HEALTHY 到達", "★ 内部HC成功・HEALTHY 到達", "Healthy (2回連続成功)", "ALBがフロント疎通確認完了！"),
        ("165秒", "稼働中", "稼働中", "★ 最悪時 HEALTHY 到達", "★ 最悪時 HEALTHY 到達", "Healthy 到達", "【最悪ケースでも165秒で完全準備完了！】\nALB 300秒期限まで『135秒もの大余裕』")
    ]

    for idx, tl in enumerate(timeline_events, start=6):
        ws4.row_dimensions[idx].height = 36 if "【" in tl[0] or "──" in tl[0] else 24
        is_sep = "───" in tl[0]
        is_fail = "【運命の境界】" in tl[0]
        is_success = "最悪ケースでも165秒" in tl[6]
        
        fill_curr = fill_section if is_sep else (fill_highlight if (is_fail or is_success) else (fill_zebra_0 if idx % 2 == 0 else fill_zebra_1))
        
        for c_idx, val in enumerate(tl):
            cell = ws4.cell(row=idx, column=c_idx+2, value=val)
            cell.font = font_bold if (is_fail or is_success or is_sep or c_idx in [0, 6]) else font_normal
            cell.fill = fill_curr
            cell.alignment = align_center if c_idx in [0, 1, 2, 5] else align_left
            cell.border = border_all


    # =============================================================
    # Sheet 5: 動作原理・歴史と背景
    # =============================================================
    ws5 = wb.create_sheet(title="5_動作原理と歴史的背景")
    ws5.views.sheetView[0].showGridLines = True
    create_title_block(ws5, "コンテナヘルスチェック・依存制御・ALB連携の動作原理と発展の歴史", 
                       "誕生の背景・なぜ各機能が必要になったのか・小学生にもわかる図解・最新技術仕様解説", max_col=8)

    ws5.cell(row=5, column=2, value="【1】 小学生にもわかるたとえ話：文化祭の模擬店（クレープ屋さん）の開店準備").font = font_section
    ws5.merge_cells(start_row=5, start_column=2, end_row=5, end_column=8)
    apply_row_style(ws5, 5, 2, 8, font=font_section, fill=fill_section, alignment=align_left, border=border_all)
    ws5.row_dimensions[5].height = 25

    story_text = (
        "みんなで文化祭で「クレープ屋さん」を開くことになりました！\n\n"
        "■ 登場人物と係の仕事：\n"
        "① ALB（校長先生のチェック）：『文化祭開始から5分後（300秒後）に見回りに来るぞ！それまでにお客さんを迎えられる状態になっていなかったら失格だ！』\n"
        "② ADOT Collector（レジ・売上ノート係）：電卓とノートを用意する係。10秒ですぐ準備完了！\n"
        "③ CloudWatch Agent（温度計係）：冷蔵庫が冷えているか確認する係。これもすぐ完了！\n"
        "④ バックエンドコンテナ（生地と生クリームを作る調理係）：重たい機械を使って生地を焼き、生クリームを泡立てる。時間がかかる（最大160秒）。\n"
        "⑤ フロントエンドコンテナ（注文を聞いてクレープを巻く接客係）：看板を出してメニューを並べる。これも時間がかかる（最大140秒）。\n\n"
        "■ 失敗したお店（パターン1：完全直列）：\n"
        "接客係の子が『調理係が生クリームを完成させるまで、絶対に何もしないで腕組みして待つ！』と言ってサボっていました。\n"
        "調理係が160秒かけて生クリームを完成させたあと、ようやく接客係がのんびり看板を並べ始めました（さらに140秒かかる）。\n"
        "合計時間：10秒 ＋ 160秒 ＋ 140秒 ＝ 310秒！\n"
        "5分（300秒）経った瞬間に校長先生（ALB）がやってきて『まだ看板の準備中じゃないか！失格だ、お店を解散しなさい！』と怒られてしまいました！\n\n"
        "■ 大成功したお店（パターン2：並列準備＋賢い声かけ）：\n"
        "接客係の子は、最初から調理係と同時に自分の看板やメニューを並べ始めました（並列起動）。\n"
        "そして、看板を並べながら調理係に『生クリームできた〜？』と声をかけて確認しました（内部ヘルスチェック：localhost:18080/healthcheck）。\n"
        "一番時間のかかる調理係が160秒でできた時、接客係の準備もすでに終わっていました！\n"
        "合計時間：たったの165秒！\n"
        "校長先生（ALB）が5分（300秒）経って見回りに来たときには、完璧な笑顔でお客さんを迎える準備ができていて、大絶賛されました！"
    )
    ws5.merge_cells(start_row=6, start_column=2, end_row=6, end_column=8)
    cell_story = ws5.cell(row=6, column=2, value=story_text)
    cell_story.font = font_normal
    cell_story.alignment = align_left
    cell_story.fill = fill_zebra_0
    apply_row_style(ws5, 6, 2, 8, font=font_normal, fill=fill_zebra_0, alignment=align_left, border=border_all)
    ws5.row_dimensions[6].height = 240

    # Section 2: 歴史と背景
    ws5.cell(row=8, column=2, value="【2】 コンテナヘルスチェックと依存関係制御の歴史と背景").font = font_section
    ws5.merge_cells(start_row=8, start_column=2, end_row=8, end_column=8)
    apply_row_style(ws5, 8, 2, 8, font=font_section, fill=fill_section, alignment=align_left, border=border_all)
    ws5.row_dimensions[8].height = 25

    history_text = (
        "■ 1. 暗黒期（2013年〜2015年：Docker初期）：ブラックボックスとしてのコンテナ\n"
        "   初期のDockerは「PID 1のプロセスが動いているかどうか」しか監視できませんでした。\n"
        "   しかしJava/JBossのような重量級システムでは、PID 1のプロセスが起動していても、内部でクラスロード中だったり、\n"
        "   OutOfMemoryErrorでスレッドが死滅していたり、デプロイに失敗していても「稼働中（Running）」と誤認される致命的な問題がありました。\n\n"
        "■ 2. ヘルスチェックの夜明け（2016年 Docker 1.12）：HEALTHCHECK命令の導入\n"
        "   コンテナ自身が内側から自分の健全性を調べる「HEALTHCHECK」命令が導入されました。\n"
        "   しかし初期仕様には「startPeriod（起動猶予）」が存在せず、起動に60秒かかるJBossは、起動の途中でヘルスチェックに3回連続失敗し、\n"
        "   「UNHEALTHY」と判定されて殺されるという悲劇が多発しました。\n\n"
        "■ 3. startPeriodの誕生（2017年 Docker 17.05 / 2018年 ECS対応）：\n"
        "   『起動中の失敗はペナルティにカウントしない』という革命的な仕組み「startPeriod」が追加されました。\n"
        "   重要なのは「startPeriodは単なるスリープタイマーではない」という点です。期間中もチェックは実行されており、\n"
        "   1度でも成功した瞬間に直ちにHEALTHYへと昇格し、startPeriodは即時終了します。\n\n"
        "■ 4. コンテナ依存制御の革新（2019年11月 AWS ECS Container Ordering）：\n"
        "   かつてECSタスク内のコンテナはすべて同時に起動するしかありませんでした。\n"
        "   サイドカー（ADOT, Envoy, メトリクス収集）が準備完了する前にアプリが起動してトレースが消える問題に対処するため、\n"
        "   「dependsOn (START / HEALTHY / COMPLETE / SUCCESS)」がAWSによって導入されました。"
    )
    ws5.merge_cells(start_row=9, start_column=2, end_row=9, end_column=8)
    cell_hist = ws5.cell(row=9, column=2, value=history_text)
    cell_hist.font = font_normal
    cell_hist.alignment = align_left
    cell_hist.fill = fill_zebra_1
    apply_row_style(ws5, 9, 2, 8, font=font_normal, fill=fill_zebra_1, alignment=align_left, border=border_all)
    ws5.row_dimensions[9].height = 200

    # Section 3: 動作原理の深堀り
    ws5.cell(row=11, column=2, value="【3】 アーキテクチャ動作原理の深堀り（ALBとECSの通信・awsvpcネットワーク）").font = font_section
    ws5.merge_cells(start_row=11, start_column=2, end_row=11, end_column=8)
    apply_row_style(ws5, 11, 2, 8, font=font_section, fill=fill_section, alignment=align_left, border=border_all)
    ws5.row_dimensions[11].height = 25

    principles_text = (
        "■ 1. ECS Fargateにおける `awsvpc` ネットワークと localhost 疎通の原理：\n"
        "   Fargateでは各タスクに専用のElastic Network Interface (ENI) が1つ割り当てられます。\n"
        "   タスク内の全コンテナ（フロント、バック、ADOT、CloudWatch Agent）は同一のネットワーク名前空間と同一のIPアドレスを共有します。\n"
        "   したがって、フロントコンテナからバックエンドへは『https://localhost:18080』で外部ネットワークを経由せず極小レイテンシで通信できます。\n\n"
        "■ 2. コンテナヘルスチェック vs ALBヘルスチェックの役割分担：\n"
        "   ・コンテナヘルスチェック（ECSエージェント管轄）：タスクの内部で実行され、コンテナが生きているか、依存先と話せるかを判定します。\n"
        "   ・ALBターゲットグループヘルスチェック（ALB管轄）：VPCの外側/ロードバランサノードからタスクのENIに向けてHTTPリクエストを送信します。\n"
        "   ALBはバックコンテナやADOTの存在を知りません。ALBが見ているのは「フロントコンテナの公開ポート」だけです。\n\n"
        "■ 3. healthCheckGracePeriodSeconds の正確な動作メカニズム：\n"
        "   タスクがRUNNING状態になってから Grace Period 秒の間、ECSサービススケジューラは「ALBがUnhealthyと報告してきてもタスクを強制終了しない」\n"
        "   という保護フィルターをかけます。しかしGrace Periodが1秒でも切れた瞬間にUnhealthyであれば即座にタスク終了シグナル(SIGTERM)が発行されます。\n"
        "   そのため、『タスク全体の完全起動時間 ＋ ALB連続成功時間（Interval×HealthyThreshold）』よりもGrace Periodが大きく設計されていなければなりません。"
    )
    ws5.merge_cells(start_row=12, start_column=2, end_row=12, end_column=8)
    cell_prin = ws5.cell(row=12, column=2, value=principles_text)
    cell_prin.font = font_normal
    cell_prin.alignment = align_left
    cell_prin.fill = fill_zebra_0
    apply_row_style(ws5, 12, 2, 8, font=font_normal, fill=fill_zebra_0, alignment=align_left, border=border_all)
    ws5.row_dimensions[12].height = 180

    # -------------------------------------------------------------
    # Auto-adjust column widths across all sheets
    # -------------------------------------------------------------
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.value:
                    val_str = str(cell.value)
                    # 改行がある場合は各行の最大長を考慮
                    lines = val_str.split("\n")
                    for l in lines:
                        # 全角文字はおよそ2文字換算
                        length = sum(2 if ord(c) > 127 else 1 for c in l)
                        if length > max_len:
                            max_len = length
            # マージセルの極端な長さを防ぐ
            col_width = min(max(max_len + 3, 12), 48)
            ws.column_dimensions[col_letter].width = col_width

    # 特別に各シートの列幅を調整
    ws1.column_dimensions["A"].width = 4
    ws1.column_dimensions["B"].width = 24
    ws1.column_dimensions["C"].width = 30
    ws1.column_dimensions["D"].width = 24
    ws1.column_dimensions["E"].width = 22
    ws1.column_dimensions["F"].width = 24
    ws1.column_dimensions["G"].width = 38
    ws1.column_dimensions["H"].width = 38

    ws2.column_dimensions["A"].width = 22
    ws2.column_dimensions["B"].width = 12
    ws2.column_dimensions["C"].width = 22
    ws2.column_dimensions["D"].width = 14
    ws2.column_dimensions["E"].width = 14
    ws2.column_dimensions["F"].width = 44
    ws2.column_dimensions["G"].width = 14
    ws2.column_dimensions["H"].width = 14
    ws2.column_dimensions["I"].width = 12
    ws2.column_dimensions["J"].width = 16

    ws3.column_dimensions["A"].width = 4
    ws3.column_dimensions["B"].width = 30
    ws3.column_dimensions["C"].width = 14
    ws3.column_dimensions["D"].width = 14
    ws3.column_dimensions["E"].width = 18
    ws3.column_dimensions["F"].width = 30
    ws3.column_dimensions["G"].width = 18
    ws3.column_dimensions["H"].width = 18

    ws4.column_dimensions["A"].width = 4
    ws4.column_dimensions["B"].width = 16
    ws4.column_dimensions["C"].width = 26
    ws4.column_dimensions["D"].width = 26
    ws4.column_dimensions["E"].width = 32
    ws4.column_dimensions["F"].width = 32
    ws4.column_dimensions["G"].width = 30
    ws4.column_dimensions["H"].width = 36

    ws5.column_dimensions["A"].width = 4
    ws5.column_dimensions["B"].width = 22
    ws5.column_dimensions["C"].width = 18
    ws5.column_dimensions["D"].width = 18
    ws5.column_dimensions["E"].width = 18
    ws5.column_dimensions["F"].width = 18
    ws5.column_dimensions["G"].width = 18
    ws5.column_dimensions["H"].width = 18

    wb.save(filename)
    print(f"Workbook successfully saved to {filename}")

if __name__ == "__main__":
    build_excel_guide()
