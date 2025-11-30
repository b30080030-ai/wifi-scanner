#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json
import os
import sys
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
except ImportError:
    print("جاري تثبيت المكتبات...")
    os.system("pip install rich")
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box

console = Console()

# البانر
BANNER = """
╦ ╦╦╔═╗╦  ╔═╗╔═╗╔═╗╔╗╔╔╗╔╔═╗╦═╗
║║║║╠╣ ║  ╚═╗║  ╠═╣║║║║║║║╣ ╠╦╝
╚╩╝╩╚  ╩  ╚═╝╚═╝╩ ╩╝╚╝╝╚╝╚═╝╩╚═
    [ كاشف شبكات WiFi - Termux ]
"""

def clear_screen():
    os.system('clear')

def show_banner():
    clear_screen()
    console.print(Panel(
        Text(BANNER, style="bold cyan", justify="center"),
        border_style="cyan",
        box=box.DOUBLE
    ))
    console.print()

def get_signal_bars(level):
    """تحويل قوة الإشارة لأشكال"""
    if level >= -50:
        return "█████", "[bold green]ممتاز[/]"
    elif level >= -60:
        return "████░", "[green]جيد جداً[/]"
    elif level >= -70:
        return "███░░", "[yellow]جيد[/]"
    elif level >= -80:
        return "██░░░", "[orange1]متوسط[/]"
    else:
        return "█░░░░", "[red]ضعيف[/]"

def get_security_icon(security):
    """أيقونة الحماية"""
    if "WPA3" in security:
        return "🔐", "[bold green]WPA3[/]"
    elif "WPA2" in security:
        return "🔒", "[green]WPA2[/]"
    elif "WPA" in security:
        return "🔒", "[yellow]WPA[/]"
    elif "WEP" in security:
        return "⚠️", "[red]WEP (ضعيف)[/]"
    else:
        return "🔓", "[bold red]مفتوحة![/]"

def get_frequency_band(freq):
    """تحديد نطاق التردد"""
    if freq >= 5000:
        return "5GHz 📶"
    else:
        return "2.4GHz 📡"

def scan_wifi():
    """فحص شبكات WiFi"""
    show_banner()
    
    console.print("[bold yellow]⏳ جاري البحث عن الشبكات...[/]\n")
    
    try:
        # تنفيذ أمر termux-wifi-scaninfo
        result = subprocess.run(
            ['termux-wifi-scaninfo'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            console.print("[bold red]❌ خطأ: تأكد من تثبيت Termux:API[/]")
            console.print("[yellow]شغّل: pkg install termux-api[/]")
            return
        
        networks = json.loads(result.stdout)
        
        if not networks:
            console.print("[yellow]⚠️ لم يتم العثور على شبكات[/]")
            return
        
        # ترتيب حسب قوة الإشارة
        networks.sort(key=lambda x: x.get('level', -100), reverse=True)
        
        # إنشاء الجدول
        table = Table(
            title="📡 الشبكات المكتشفة",
            box=box.ROUNDED,
            border_style="cyan",
            header_style="bold white on blue"
        )
        
        table.add_column("#", style="dim", width=3, justify="center")
        table.add_column("اسم الشبكة (SSID)", style="bold white", min_width=20)
        table.add_column("الإشارة", justify="center", width=8)
        table.add_column("القوة", justify="center", width=12)
        table.add_column("الحماية", justify="center", width=15)
        table.add_column("التردد", justify="center", width=10)
        table.add_column("MAC", style="dim", width=17)
        
        for i, network in enumerate(networks, 1):
            ssid = network.get('ssid', 'مخفي') or '[مخفي]'
            bssid = network.get('bssid', 'N/A')
            level = network.get('level', -100)
            freq = network.get('frequency', 0)
            capabilities = network.get('capabilities', '')
            
            # الحصول على المعلومات المرئية
            bars, strength = get_signal_bars(level)
            sec_icon, sec_text = get_security_icon(capabilities)
            band = get_frequency_band(freq)
            
            # تلوين اسم الشبكة
            if ssid == '[مخفي]':
                ssid_display = f"[dim italic]{ssid}[/]"
            else:
                ssid_display = f"[bold]{ssid}[/]"
            
            table.add_row(
                str(i),
                ssid_display,
                f"[cyan]{bars}[/]",
                f"{strength} ({level}dBm)",
                f"{sec_icon} {sec_text}",
                band,
                bssid
            )
        
        console.print(table)
        console.print()
        
        # إحصائيات
        stats_table = Table(box=box.SIMPLE, show_header=False)
        stats_table.add_column("", style="cyan")
        stats_table.add_column("")
        
        total = len(networks)
        open_nets = sum(1 for n in networks if 'WPA' not in n.get('capabilities', '') and 'WEP' not in n.get('capabilities', ''))
        secured = total - open_nets
        
        stats_table.add_row("📊 إجمالي الشبكات:", f"[bold]{total}[/]")
        stats_table.add_row("🔒 شبكات محمية:", f"[green]{secured}[/]")
        stats_table.add_row("🔓 شبكات مفتوحة:", f"[red]{open_nets}[/]")
        stats_table.add_row("🕐 وقت الفحص:", datetime.now().strftime("%H:%M:%S"))
        
        console.print(Panel(stats_table, title="📈 إحصائيات", border_style="green"))
        
    except subprocess.TimeoutExpired:
        console.print("[red]❌ انتهت مهلة الفحص[/]")
    except json.JSONDecodeError:
        console.print("[red]❌ خطأ في قراءة البيانات[/]")
    except FileNotFoundError:
        console.print("[red]❌ termux-wifi-scaninfo غير موجود[/]")
        console.print("[yellow]ثبّت Termux:API من F-Droid[/]")
    except Exception as e:
        console.print(f"[red]❌ خطأ: {e}[/]")

def main_menu():
    """القائمة الرئيسية"""
    while True:
        show_banner()
        
        menu = Table(box=box.ROUNDED, show_header=False, border_style="cyan")
        menu.add_column("", justify="center")
        
        menu.add_row("[bold cyan]═══ القائمة الرئيسية ═══[/]")
        menu.add_row("")
        menu.add_row("[1] 📡 فحص الشبكات")
        menu.add_row("[2] 🔄 فحص مستمر (كل 10 ثواني)")
        menu.add_row("[3] 📋 معلومات WiFi الحالي")
        menu.add_row("[0] 🚪 خروج")
        menu.add_row("")
        
        console.print(menu)
        
        choice = console.input("\n[bold yellow]➤ اختر: [/]")
        
        if choice == "1":
            scan_wifi()
            console.input("\n[dim]اضغط Enter للمتابعة...[/]")
        
        elif choice == "2":
            console.print("[yellow]🔄 وضع الفحص المستمر (Ctrl+C للإيقاف)[/]")
            try:
                import time
                while True:
                    scan_wifi()
                    console.print("[dim]⏳ الفحص القادم بعد 10 ثواني...[/]")
                    time.sleep(10)
            except KeyboardInterrupt:
                console.print("\n[yellow]⏹️ تم الإيقاف[/]")
                console.input("[dim]اضغط Enter للمتابعة...[/]")
        
        elif choice == "3":
            show_current_wifi()
            console.input("\n[dim]اضغط Enter للمتابعة...[/]")
        
        elif choice == "0":
            console.print("[bold green]👋 إلى اللقاء![/]")
            sys.exit(0)

def show_current_wifi():
    """عرض معلومات الشبكة الحالية"""
    show_banner()
    try:
        result = subprocess.run(
            ['termux-wifi-connectioninfo'],
            capture_output=True,
            text=True
        )
        
        info = json.loads(result.stdout)
        
        table = Table(title="📱 الشبكة المتصلة حالياً", box=box.ROUNDED)
        table.add_column("المعلومة", style="cyan")
        table.add_column("القيمة", style="white")
        
        table.add_row("اسم الشبكة", info.get('ssid', 'N/A'))
        table.add_row("BSSID", info.get('bssid', 'N/A'))
        table.add_row("قوة الإشارة", f"{info.get('rssi', 'N/A')} dBm")
        table.add_row("التردد", f"{info.get('frequency_mhz', 'N/A')} MHz")
        table.add_row("IP", info.get('ip', 'N/A'))
        table.add_row("سرعة الاتصال", f"{info.get('link_speed_mbps', 'N/A')} Mbps")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]❌ خطأ: {e}[/]")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 تم الإيقاف[/]")
