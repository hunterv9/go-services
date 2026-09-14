"""
Gemini Chat Proxy — Professional CLI Assistant
Thiết kế giao diện phong cách Infrabases CLI (Rich Console, Panels, Menu, Spinners)
Client → Cloudflare Worker Proxy / Russia PHP Proxy → Vietnam Wanderer API → Gemini
"""

import os
import sys
import time
import requests
import concurrent.futures
from datetime import datetime

# Đảm bảo console UTF-8 trên Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

console = Console()

# ================= CẤU HÌNH HỆ THỐNG =================
PERSONAS = {
    "general": {
        "name": "Trợ Lý Đa Năng Thông Minh",
        "prompt": "You are a brilliant, helpful, versatile AI assistant. Answer clearly, accurately, and politely across all domains. Do not assume any travel or tourism persona.",
    },
    "developer": {
        "name": "Kỹ Sư Phần Mềm / Lập Trình Viên",
        "prompt": "You are a senior software architect and coding expert. Provide clean, well-structured, production-ready code with concise explanations. Focus on best practices, algorithms, and security. Do not assume any travel or tourism persona.",
    },
    "translator": {
        "name": "Chuyên Gia Dịch Thuật Đa Ngôn Ngữ",
        "prompt": "You are a master translator. Translate text accurately, naturally, and context-aware, preserving nuances and tone without adding commentary.",
    },
    "analyst": {
        "name": "Chuyên Gia Phân Tích Dữ Liệu & Logic",
        "prompt": "You are a data analyst and critical thinker. Break down complex problems, analyze step-by-step, and provide structured insights with facts and logic.",
    },
    "travel": {
        "name": "Trợ Lý Du Lịch Việt Nam (Gốc)",
        "prompt": "You are a local Vietnam travel guide. Share travel insights, foods, budgets, and tips for exploring Vietnam.",
    },
}

CONFIG = {
    "cloudflare_proxy": "https://young-limit-d9be.hoangblack3345.workers.dev/",
    "russia_proxy": "https://sub.bookshaadi.com/",
    "direct_api": "https://vietnam-wanderer-141277360286.asia-southeast1.run.app/api/gemini/chat",
    "active_gateway": "cloudflare",  # cloudflare | russia | direct
    "active_persona": "developer",   # general | developer | translator | analyst | travel | custom
    "custom_persona_prompt": "",
    "language": "vi",
    "timeout": 45,
}

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Lưu trữ lịch sử hội thoại trong phiên
CONVERSATION_HISTORY = []


def get_active_url() -> str:
    """Trả về endpoint tương ứng với gateway đang kích hoạt."""
    gw = CONFIG["active_gateway"]
    if gw == "cloudflare":
        return CONFIG["cloudflare_proxy"]
    elif gw == "russia":
        return CONFIG["russia_proxy"]
    else:
        return CONFIG["direct_api"]


def get_gateway_name() -> str:
    """Tên thân thiện của gateway hiện tại."""
    names = {
        "cloudflare": "Cloudflare Worker Proxy (Tối ưu)",
        "russia": "PHP Proxy Server Nga",
        "direct": "Gọi trực tiếp (Asia-Southeast1)",
    }
    return names.get(CONFIG["active_gateway"], "Custom")


def get_current_system_prompt() -> str:
    """Lấy system prompt tương ứng với vai trò (persona) đang chọn."""
    key = CONFIG.get("active_persona", "general")
    if key == "custom" and CONFIG.get("custom_persona_prompt"):
        return CONFIG["custom_persona_prompt"]
    return PERSONAS.get(key, PERSONAS["general"])["prompt"]


def get_persona_name() -> str:
    """Tên hiển thị của vai trò hiện tại."""
    key = CONFIG.get("active_persona", "general")
    if key == "custom":
        return "Tùy Chỉnh (Custom)"
    return PERSONAS.get(key, {}).get("name", "Đa Năng")


def _cli_friendly_error(exc: Exception) -> str:
    """Chuyển đổi lỗi kỹ thuật thành tiếng Việt dễ hiểu."""
    msg = str(exc).lower()
    if "timeout" in msg or "timed out" in msg:
        return "Kết nối quá thời gian quy định (Timeout). Máy chủ phản hồi chậm hoặc đang quá tải."
    if "connection" in msg or "failed to establish" in msg or "network" in msg:
        return "Không thể kết nối đến Gateway. Vui lòng kiểm tra internet hoặc đổi Gateway trong Menu."
    if "403" in msg or "forbidden" in msg:
        return "Gateway từ chối yêu cầu (403 Forbidden). Có thể IP bị chặn hoặc proxy lỗi."
    if "404" in msg or "not found" in msg:
        return "Không tìm thấy API endpoint (404 Not Found)."
    if "500" in msg or "502" in msg or "503" in msg:
        return "Máy chủ Gemini hoặc Gateway gặp lỗi nội bộ (5xx Server Error)."
    return str(exc)


def print_banner():
    """Banner phong cách Infrabases / Dowloadapi."""
    banner_ascii = r"""[bold cyan]
  ██████╗ ███████╗███╗   ███╗██╗███╗   ██╗██╗     ██████╗██╗     ██╗
 ██╔════╝ ██╔════╝████╗ ████║██║████╗  ██║██║    ██╔════╝██║     ██║
 ██║  ███╗█████╗  ██╔████╔██║██║██╔██╗ ██║██║    ██║     ██║     ██║
 ██║   ██║██╔══╝  ██║╚██╔╝██║██║██║╚██╗██║██║    ██║     ██║     ██║
 ╚██████╔╝███████╗██║ ╚═╝ ██║██║██║ ╚═╝██║██║    ╚██████╗███████╗██║
  ╚═════╝ ╚══════╝╚═╝     ╚═╝╚═╝╚═╝     ╚═╝╚═╝     ╚═════╝╚══════╝╚═╝
[/bold cyan]
[dim]• Gemini AI Universal Assistant • Clean System Form • Ultra Low Latency •[/dim]
"""
    banner_footer = (
        f"[bold green][+][/bold green] [bold white]GEMINI UNIVERSAL ASSISTANT (UNLOCKED)[/bold white]\n"
        f"[dim]Gateway:[/dim] [cyan]{get_gateway_name()}[/cyan]  "
        f"[dim]• Vai trò:[/dim] [magenta]{get_persona_name()}[/magenta]  "
        f"[dim]• Ngôn ngữ:[/dim] [yellow]{CONFIG['language'].upper()}[/yellow]"
    )
    console.print(
        Panel.fit(
            banner_ascii + "\n" + banner_footer,
            border_style="green",
            padding=(1, 4),
        )
    )


def chat_api(message: str, language: str = None, history: list = None) -> str:
    """Gửi payload hỗ trợ cả form cũ (provinceName) lẫn form mới (system fields)."""
    url = get_active_url()
    sys_prompt = get_current_system_prompt()
    clean_history = history[-6:] if history else []

    payload = {
        "message": message,
        "language": language or CONFIG["language"],
        "provinceName": f"None\n[System Instruction: {sys_prompt}]",
        "region": "All Regions",
        "history": clean_history,
        # Form mới: gửi persona qua field riêng, server dùng field nào thì nhận field đó.
        "system": sys_prompt,
        "systemPrompt": sys_prompt,
        "systemInstruction": sys_prompt,
        "instructions": sys_prompt,
        "persona": sys_prompt,
    }

    resp = requests.post(url, headers=HEADERS, json=payload, timeout=CONFIG["timeout"])
    resp.raise_for_status()

    data = resp.json()
    return data.get("reply", "(Không có nội dung phản hồi từ AI)")


def display_reply_panel(reply_text: str, elapsed: float, model_title: str = "Gemini AI"):
    """Hiển thị nội dung trả lời trong khung Panel sang trọng."""
    md = Markdown(reply_text)
    time_str = datetime.now().strftime("%H:%M:%S")
    console.print(
        Panel(
            md,
            title=f"[bold green]✔ {model_title}[/bold green]",
            subtitle=f"[dim cyan]⏱ {elapsed:.2f}s • {time_str}[/dim cyan]",
            border_style="bright_blue",
            padding=(1, 2),
        )
    )


def select_persona_menu():
    """Menu chọn vai trò AI (Persona)."""
    console.print("\n[bold cyan]Danh sách vai trò (Persona) có sẵn:[/bold cyan]")
    keys = list(PERSONAS.keys())
    for i, k in enumerate(keys, start=1):
        p = PERSONAS[k]
        active_mark = " [bold green]✔ [Đang chọn][/bold green]" if CONFIG.get("active_persona") == k else ""
        console.print(f"{i}. [bold white]{p['name']}[/bold white]{active_mark}")
    console.print(f"{len(keys)+1}. [bold yellow]Nhập vai trò tùy chỉnh (Tự viết System Prompt)...[/bold yellow]")

    choice = Prompt.ask(
        "Chọn vai trò",
        choices=[str(i) for i in range(1, len(keys) + 2)],
        default="1",
    )
    idx = int(choice) - 1
    if idx < len(keys):
        CONFIG["active_persona"] = keys[idx]
        console.print(f"[bold green]✔ Đã chuyển sang vai trò: {PERSONAS[keys[idx]]['name']}![/bold green]")
    else:
        custom_p = Prompt.ask("Nhập chỉ thị hệ thống bạn muốn AI tuân theo").strip()
        if custom_p:
            CONFIG["active_persona"] = "custom"
            CONFIG["custom_persona_prompt"] = custom_p
            console.print("[bold green]✔ Đã áp dụng System Prompt tùy chỉnh![/bold green]")
    time.sleep(1)


def handle_interactive_chat():
    """Chế độ trò chuyện tương tác theo luồng với ghi nhớ ngữ cảnh."""
    global CONVERSATION_HISTORY
    os.system("cls" if os.name == "nt" else "clear")
    print_banner()

    console.print(
        Panel.fit(
            f"[bold green]CHẾ ĐỘ TRÒ CHUYỆN TRỰC TIẾP (INTERACTIVE CHAT)[/bold green]\n"
            f"[dim]• Vai trò hiện tại: [magenta]{get_persona_name()}[/magenta]\n"
            f"• Gõ nội dung bất kỳ để trò chuyện\n"
            f"• Gõ [bold cyan]/persona[/bold cyan] để đổi vai trò (Dev, Dịch thuật, Đa năng...)\n"
            f"• Gõ [bold yellow]/clear[/bold yellow] để xoá ngữ cảnh\n"
            f"• Gõ [bold red]/back[/bold red] hoặc [bold red]exit[/bold red] để quay lại Menu chính[/dim]",
            border_style="cyan",
        )
    )

    while True:
        try:
            turn_count = len(CONVERSATION_HISTORY) // 2
            console.print(
                f"\n[bold magenta]╭─ [bold cyan]You[/bold cyan] "
                f"[dim]({datetime.now().strftime('%H:%M:%S')})[/dim] "
                f"[dim yellow]• Lượt: {turn_count}[/dim yellow][/bold magenta]"
            )
            user_input = Prompt.ask("[bold magenta]╰─❯[/bold magenta]").strip()

        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Quay lại Menu chính...[/yellow]")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        # Thoát về menu
        if cmd in ("/back", "/menu", "/exit", "/quit", "back", "exit", "quit"):
            break

        # Đổi vai trò Persona
        if cmd in ("/persona", "/role", "persona", "role"):
            select_persona_menu()
            continue

        # Trợ giúp
        if cmd in ("/help", "help"):
            table = Table(title="Danh Sách Lệnh Trong Chat", border_style="cyan")
            table.add_column("Lệnh", style="bold cyan")
            table.add_column("Chức năng", style="white")
            table.add_row("/persona", "Đổi vai trò AI (Developer, Dịch thuật, Đa năng...)")
            table.add_row("/clear", "Xoá sạch ngữ cảnh hội thoại hiện tại")
            table.add_row("/history", "Xem lại các lượt chat gần nhất")
            table.add_row("/help", "Xem bảng lệnh này")
            table.add_row("/back, /exit", "Quay lại Menu điều khiển chính")
            console.print(table)
            continue

        # Xoá ngữ cảnh
        if cmd in ("/clear", "/reset", "clear", "cls"):
            CONVERSATION_HISTORY.clear()
            console.print("[bold yellow]🧹 Đã làm mới ngữ cảnh hội thoại![/bold yellow]")
            continue

        # Xem lịch sử
        if cmd == "/history":
            show_history_table()
            continue

        # Gửi tin nhắn
        t0 = time.time()
        with console.status(
            f"[bold cyan] Gemini ({get_persona_name()}) đang xử lý câu trả lời...[/bold cyan]",
            spinner="dots12",
        ):
            try:
                reply = chat_api(user_input, history=CONVERSATION_HISTORY)
                elapsed = time.time() - t0
                display_reply_panel(reply, elapsed, model_title=f"Gemini • {get_persona_name()}")

                # Lưu vào context
                CONVERSATION_HISTORY.append({"role": "user", "text": user_input})
                CONVERSATION_HISTORY.append({"role": "model", "text": reply})

            except Exception as e:
                elapsed = time.time() - t0
                console.print(
                    Panel.fit(
                        f"[bold red]❌ Lỗi khi gửi câu hỏi:[/bold red]\n{_cli_friendly_error(e)}",
                        title="[red]Lỗi Kết Nối[/red]",
                        border_style="red",
                    )
                )


def handle_single_query():
    """Chế độ hỏi nhanh 1 câu."""
    question = Prompt.ask("\n[bold cyan]Nhập câu hỏi của bạn[/bold cyan]").strip()
    if not question:
        console.print("[red]Câu hỏi không được để trống![/red]")
        return

    t0 = time.time()
    with console.status(f"[bold cyan]Đang gửi câu hỏi đến AI ({get_persona_name()})...[/bold cyan]", spinner="dots12"):
        try:
            reply = chat_api(question, history=[])
            display_reply_panel(reply, time.time() - t0, model_title=f"Kết Quả Hỏi Nhanh • {get_persona_name()}")
        except Exception as e:
            console.print(f"\n[bold red]❌ Lỗi:[/bold red] {_cli_friendly_error(e)}")


def show_config_table():
    """Hiển thị bảng cấu hình hiện tại."""
    table = Table(title="[bold green]Cấu Hình Kết Nối & Hệ Thống[/bold green]", border_style="green")
    table.add_column("Tham số", style="cyan", width=22)
    table.add_column("Giá trị", style="yellow")
    table.add_column("Ghi chú", style="dim")

    table.add_row("Gateway đang dùng", get_gateway_name(), "[bold green]Đang hoạt động[/bold green]")
    table.add_row("Vai trò AI (Persona)", get_persona_name(), "Tự do tùy chỉnh System Prompt")
    table.add_row("Ngôn ngữ phản hồi", CONFIG["language"].upper(), "Tiếng Việt / English...")
    table.add_row("Timeout tối đa", f"{CONFIG['timeout']} giây", "Thời gian chờ tối đa")
    table.add_row("Số tin nhắn trong cache", str(len(CONVERSATION_HISTORY)), f"{len(CONVERSATION_HISTORY)//2} lượt hỏi-đáp")

    console.print(table)


def handle_settings():
    """Menu tuỳ chỉnh Gateway, Persona và Ngôn ngữ."""
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print_banner()
        show_config_table()

        console.print("\n[bold cyan]Tuỳ chọn cấu hình:[/bold cyan]")
        console.print("1. [bold white]Đổi vai trò AI (Persona)[/bold white] (Dev, Dịch thuật, Đa năng, Custom...)")
        console.print("2. [bold white]Đổi Gateway sang Cloudflare Worker Proxy[/bold white] (Mặc định, nhanh)")
        console.print("3. [bold white]Đổi Gateway sang PHP Proxy Server Nga[/bold white]")
        console.print("4. [bold white]Đổi Gateway sang Gọi trực tiếp[/bold white] (Direct Cloud Run)")
        console.print("5. [bold white]Đổi ngôn ngữ phản hồi[/bold white] (vi, en, ja, ko...)")
        console.print("6. [bold white]Xoá sạch bộ nhớ đệm lịch sử[/bold white]")
        console.print("7. [bold yellow]Quay lại Menu chính[/bold yellow]")

        choice = Prompt.ask("\nChọn chức năng", choices=["1", "2", "3", "4", "5", "6", "7"], default="7")

        if choice == "1":
            select_persona_menu()
        elif choice == "2":
            CONFIG["active_gateway"] = "cloudflare"
            console.print("[bold green]✔ Đã chuyển Gateway sang Cloudflare Worker Proxy![/bold green]")
            time.sleep(1)
        elif choice == "3":
            CONFIG["active_gateway"] = "russia"
            console.print("[bold green]✔ Đã chuyển Gateway sang Server Nga Proxy![/bold green]")
            time.sleep(1)
        elif choice == "4":
            CONFIG["active_gateway"] = "direct"
            console.print("[bold yellow]✔ Đã chuyển sang Gọi trực tiếp Direct API![/bold yellow]")
            time.sleep(1)
        elif choice == "5":
            new_lang = Prompt.ask("Nhập mã ngôn ngữ mới", default=CONFIG["language"]).strip()
            if new_lang:
                CONFIG["language"] = new_lang
                console.print(f"[bold green]✔ Đã đổi ngôn ngữ sang: {new_lang}![/bold green]")
                time.sleep(1)
        elif choice == "6":
            CONVERSATION_HISTORY.clear()
            console.print("[bold green]✔ Đã làm rỗng bộ nhớ lịch sử![/bold green]")
            time.sleep(1)
        elif choice == "7":
            break


def show_history_table():
    """Hiển thị bảng chi tiết lịch sử."""
    if not CONVERSATION_HISTORY:
        console.print("[italic dim]Lịch sử hiện tại đang trống.[/italic dim]")
        return

    table = Table(
        title=f"📜 Lịch Sử Hội Thoại ({len(CONVERSATION_HISTORY)//2} lượt)",
        border_style="cyan",
        expand=True,
    )
    table.add_column("Lượt", justify="center", width=6, style="dim")
    table.add_column("Người gửi", width=12)
    table.add_column("Nội dung tóm tắt")

    for i, msg in enumerate(CONVERSATION_HISTORY):
        turn = (i // 2) + 1
        is_user = msg["role"] == "user"
        sender = "[bold cyan]You[/bold cyan]" if is_user else "[bold green]Gemini[/bold green]"
        text_clean = msg["text"].strip().replace("\n", " ")
        if len(text_clean) > 85:
            text_clean = text_clean[:82] + "..."
        table.add_row(str(turn), sender, text_clean)

    console.print(table)


def ping_single_gateway(name: str, url: str) -> tuple:
    """Kiểm tra kết nối và đo độ trễ cho 1 Gateway đơn lẻ."""
    t0 = time.time()
    try:
        resp = requests.post(
            url,
            headers=HEADERS,
            json={"message": "ping", "language": "vi", "history": []},
            timeout=15,
        )
        elapsed_ms = (time.time() - t0) * 1000
        if resp.status_code == 200:
            return (name, f"[green]{elapsed_ms:.0f} ms[/green]", "[bold green]ONLINE (200 OK)[/bold green]")
        else:
            return (name, f"[yellow]{elapsed_ms:.0f} ms[/yellow]", f"[yellow]HTTP {resp.status_code}[/yellow]")
    except requests.exceptions.Timeout:
        return (name, "[red]> 15000 ms[/red]", "[red]TIMEOUT[/red]")
    except Exception:
        return (name, "[red]--[/red]", "[red]OFFLINE[/red]")


def handle_ping_test():
    """Kiểm tra độ trễ mạng và hiển thị kết quả ngay khi từng Gateway hoàn tất."""
    os.system("cls" if os.name == "nt" else "clear")
    print_banner()
    console.print("[bold cyan]Đang kiểm tra kết nối đồng thời — Gateway nào xong sẽ hiển thị kết quả ngay:[/bold cyan]\n")

    targets = [
        ("Cloudflare Worker", CONFIG["cloudflare_proxy"]),
        ("Server Nga PHP", CONFIG["russia_proxy"]),
        ("Direct API Run", CONFIG["direct_api"]),
    ]

    target_names = [t[0] for t in targets]
    # Khởi tạo trạng thái ban đầu cho các Gateway
    results = {name: ("[dim cyan]Đang đo...[/dim cyan]", "[yellow]⏳ Đang kiểm tra...[/yellow]") for name in target_names}

    def render_table():
        t = Table(title="[bold green]Kết Quả Kiểm Tra Kết Nối (Health Check)[/bold green]", border_style="green")
        t.add_column("Gateway", style="bold white", width=25)
        t.add_column("Độ trễ", justify="right", width=15)
        t.add_column("Trạng thái", justify="center", width=22)
        for name in target_names:
            lat, st = results[name]
            t.add_row(name, lat, st)
        return t

    with Live(render_table(), console=console, refresh_per_second=8) as live:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(targets)) as executor:
            future_to_target = {
                executor.submit(ping_single_gateway, name, url): name
                for name, url in targets
            }
            for future in concurrent.futures.as_completed(future_to_target):
                name, lat, st = future.result()
                results[name] = (lat, st)
                live.update(render_table())


def main():
    """Vòng lặp Menu chính phong cách Infrabases / Dowloadapi."""
    # Nếu truyền câu hỏi trực tiếp qua CLI
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        console.print(
            Panel.fit(
                f"[bold cyan]Câu hỏi:[/bold cyan] {question}",
                title="[bold yellow] Gemini One-Shot[/bold yellow]",
                border_style="yellow",
            )
        )
        t0 = time.time()
        with console.status("[bold cyan] Đang xử lý câu hỏi...[/bold cyan]", spinner="dots12"):
            try:
                ans = chat_api(question)
                display_reply_panel(ans, time.time() - t0)
            except Exception as e:
                console.print(f"[bold red]❌ Lỗi:[/bold red] {_cli_friendly_error(e)}")
        return

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print_banner()

        console.print("[bold green]=== MENU ĐIỀU KHIỂN ===[/bold green]")
        console.print("1. [bold white]Bắt đầu trò chuyện[/bold white] (Interactive Chat)")
        console.print("2. [bold white]Hỏi nhanh 1 câu[/bold white] (Quick Query)")
        console.print("3. [bold white]Cấu hình Gateway & Proxy[/bold white] (Cloudflare / Nga / Direct)")
        console.print("4. [bold white]Lịch sử hội thoại[/bold white] (Xem tin nhắn đã lưu)")
        console.print("5. [bold white]Kiểm tra kết nối Gateway[/bold white] (Ping Test)")
        console.print("6. [bold red]Thoát[/bold red]")

        choice = Prompt.ask("\nNhập lựa chọn của bạn", choices=["1", "2", "3", "4", "5", "6"], default="1")

        if choice == "1":
            handle_interactive_chat()
            Prompt.ask("\n[dim]Nhấn Enter để quay lại menu...[/dim]")
        elif choice == "2":
            handle_single_query()
            Prompt.ask("\n[dim]Nhấn Enter để tiếp tục...[/dim]")
        elif choice == "3":
            handle_settings()
        elif choice == "4":
            os.system("cls" if os.name == "nt" else "clear")
            print_banner()
            show_history_table()
            Prompt.ask("\n[dim]Nhấn Enter để quay lại menu...[/dim]")
        elif choice == "5":
            handle_ping_test()
            Prompt.ask("\n[dim]Nhấn Enter để quay lại menu...[/dim]")
        elif choice == "6":
            console.print(
                Panel.fit(
                    "[bold green]Cảm ơn bạn đã sử dụng Vietnam Wanderer Gemini Assistant!\nHẹn gặp lại! ✨[/bold green]",
                    border_style="green",
                    padding=(1, 4),
                )
            )
            break


if __name__ == "__main__":
    main()
