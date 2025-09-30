import os
import logging
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import schedule
import time

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AshewaCampaignBot:
    def __init__(self):
        self.token = os.getenv('ASHEWA_BOT_TOKEN')
        if not self.token:
            logger.error("❌ ASHEWA_BOT_TOKEN not found!")
            raise ValueError("Please set ASHEWA_BOT_TOKEN environment variable")
        
        self.updater = Updater(self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.setup_handlers()
        self.init_db()
        
        # Campaign data
        self.campaign_data = {
            'revenue_target': 131000000,
            'campaigns': [
                {
                    'name': 'Bundled Packages',
                    'budget': 2500000,
                    'kpi': '20 ERP deals = 40M Br',
                    'timeline': '2 weeks',
                    'team': 'Sales Team'
                },
                {
                    'name': 'Brand Campaign', 
                    'budget': 4000000,
                    'kpi': '1M reach, 2K MQLs, 15K calls',
                    'timeline': '2 weeks', 
                    'team': 'Marketing Team'
                }
            ]
        }
        
        logger.info("🤖 Ashewa Campaign Bot Initialized!")

    def init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect('ashewa_campaign.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS campaign_progress
                     (id INTEGER PRIMARY KEY, start_date TEXT, current_revenue REAL, updated_at TEXT)''')
        conn.commit()
        conn.close()

    def setup_handlers(self):
        """Setup bot command handlers"""
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("campaign", self.show_campaign))
        self.dispatcher.add_handler(CommandHandler("progress", self.show_progress))
        self.dispatcher.add_handler(CommandHandler("targets", self.show_targets))
        self.dispatcher.add_handler(CommandHandler("revenue", self.show_revenue))
        self.dispatcher.add_handler(CommandHandler("milestone", self.next_milestone))
        self.dispatcher.add_handler(CommandHandler("motivate", self.send_motivation))

    def get_db_connection(self):
        return sqlite3.connect('ashewa_campaign.db')

    def start(self, update: Update, context: CallbackContext):
        """Start command - initialize campaign"""
        welcome_message = """
🏁 **ASHEWA 90-DAY MARKETING CAMPAIGN TRACKER** 🏁

*"Built Here, By Ethiopians, For Ethiopia's Digital Future"*

🎯 **Campaign Goal:** 131M Br Revenue in 90 Days
📅 **Theme:** "One Platform. Endless Possibilities. Made for Ethiopia."

**Available Commands:**
/campaign - Show all campaigns
/progress - Overall progress
/targets - Team daily/weekly targets  
/revenue - Revenue tracking
/milestone - Next milestones
/motivate - Team motivation

*Let's build Ethiopia's digital future together!* 🇪🇹
        """
        
        # Initialize campaign if not exists
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM campaign_progress LIMIT 1")
        if not c.fetchone():
            start_date = datetime.now().strftime("%Y-%m-%d")
            c.execute("INSERT INTO campaign_progress (start_date, current_revenue, updated_at) VALUES (?, ?, ?)",
                     (start_date, 0, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
        
        conn.close()
        
        update.message.reply_text(welcome_message, parse_mode='Markdown')

    def show_campaign(self, update: Update, context: CallbackContext):
        """Show all marketing campaigns"""
        campaign_msg = "🎯 **ASHEWA 90-DAY MARKETING CAMPAIGNS**\n\n"
        
        for i, campaign in enumerate(self.campaign_data['campaigns'], 1):
            campaign_msg += f"**{i}. {campaign['name']}**\n"
            campaign_msg += f"   💰 Budget: {campaign['budget']:,} Br\n"
            campaign_msg += f"   🎯 KPI: {campaign['kpi']}\n"
            campaign_msg += f"   ⏰ Timeline: {campaign['timeline']}\n"
            campaign_msg += f"   👥 Team: {campaign['team']}\n\n"
        
        update.message.reply_text(campaign_msg, parse_mode='Markdown')

    def show_progress(self, update: Update, context: CallbackContext):
        """Show overall campaign progress"""
        conn = self.get_db_connection()
        c = conn.cursor()
        
        c.execute("SELECT start_date, current_revenue FROM campaign_progress LIMIT 1")
        result = c.fetchone()
        
        if result:
            start_date = datetime.strptime(result[0], "%Y-%m-%d")
            current_revenue = result[1]
            days_passed = (datetime.now() - start_date).days
        else:
            days_passed = 0
            current_revenue = 0
        
        days_remaining = 90 - days_passed
        progress_percent = (days_passed / 90) * 100
        revenue_percent = (current_revenue / self.campaign_data['revenue_target']) * 100
        
        progress_msg = f"""
⏰ **90-DAY CAMPAIGN PROGRESS**

📅 **Time Progress:** {days_passed}/90 days ({progress_percent:.1f}%)
💰 **Revenue Progress:** {current_revenue:,.0f} Br / {self.campaign_data['revenue_target']:,.0f} Br ({revenue_percent:.1f}%)
⏳ **Days Remaining:** {days_remaining}

{self.create_progress_bar(progress_percent)}

**Quick Stats:**
• Daily Revenue Target: {self.campaign_data['revenue_target']/90:,.0f} Br/day
• Revenue Needed: {self.campaign_data['revenue_target'] - current_revenue:,.0f} Br
        """
        
        update.message.reply_text(progress_msg, parse_mode='Markdown')
        conn.close()

    def create_progress_bar(self, percentage):
        bars = 20
        filled_bars = int((percentage / 100) * bars)
        empty_bars = bars - filled_bars
        return f"▓" * filled_bars + f"░" * empty_bars + f" {percentage:.1f}%"

    def show_targets(self, update: Update, context: CallbackContext):
        """Show team targets"""
        targets_msg = """
👥 **TEAM DAILY TARGETS**

**Sales Team:**
📋 Follow up 20-25 hot leads
🎯 Weekly: Close 2-3 ERP deals

**Marketing Team:**
📋 Launch 3-5 social ads  
🎯 Weekly: Generate 200-300 MQLs

**BD Team:**
📋 Schedule 5-10 C-level demos
🎯 Weekly: Close 1-2 enterprise deals

**All Teams: Push for 131M Br target! 💪**
        """
        update.message.reply_text(targets_msg, parse_mode='Markdown')

    def show_revenue(self, update: Update, context: CallbackContext):
        """Show revenue tracking"""
        conn = self.get_db_connection()
        c = conn.cursor()
        
        c.execute("SELECT current_revenue FROM campaign_progress LIMIT 1")
        current_revenue = c.fetchone()[0] if c.fetchone() else 0
        
        revenue_msg = f"""
💰 **REVENUE TRACKING**

**Overall Target:** 131,000,000 Br
**Current Revenue:** {current_revenue:,.0f} Br
**Remaining:** {self.campaign_data['revenue_target'] - current_revenue:,.0f} Br
**Completion:** {(current_revenue/self.campaign_data['revenue_target'])*100:.1f}%

**Daily Target:** {self.campaign_data['revenue_target']/90:,.0f} Br/day

*Keep pushing! Every deal counts!* 🚀
        """
        
        update.message.reply_text(revenue_msg, parse_mode='Markdown')
        conn.close()

    def next_milestone(self, update: Update, context: CallbackContext):
        """Show next milestones"""
        conn = self.get_db_connection()
        c = conn.cursor()
        
        c.execute("SELECT start_date FROM campaign_progress LIMIT 1")
        result = c.fetchone()
        
        if result:
            start_date = datetime.strptime(result[0], "%Y-%m-%d")
            days_passed = (datetime.now() - start_date).days
        else:
            days_passed = 0
        
        milestones = {
            7: "🎊 Complete Week 1 - Initial campaign results",
            30: "🚀 One Month - 25% revenue target (32.75M Br)",
            45: "⚡ Halfway Point - 50% revenue target (65.5M Br)", 
            60: "🎯 Two Months - ABM campaign completion",
            90: "🏆 Campaign Complete - 131M Br Target!"
        }
        
        next_milestone_day = None
        for day in sorted(milestones.keys()):
            if days_passed < day:
                next_milestone_day = day
                break
        
        if next_milestone_day:
            days_to_go = next_milestone_day - days_passed
            milestone_msg = f"""
🎯 **NEXT MILESTONE**

**Day {next_milestone_day}:** {milestones[next_milestone_day]}
**Days to go:** {days_to_go}

*Stay focused! We're building Ethiopia's digital future!* 🇪🇹
            """
        else:
            milestone_msg = "🎉 All milestones completed! Campaign finished!"
        
        update.message.reply_text(milestone_msg, parse_mode='Markdown')
        conn.close()

    def send_motivation(self, update: Update, context: CallbackContext):
        """Send motivational messages"""
        motivations = [
            "🚀 **Together, we build our future!** Keep pushing for Ethiopia's digital transformation!",
            "💫 **One Platform, All Your Needs** - Remember why we're doing this!",
            "🏆 **Built Here, By Ethiopians, For Ethiopia** - You're making history!",
            "🎯 **131M Br target is within reach!** Every call, every demo, every deal matters!",
            "⚡ **Digitize, Simplify, Empower with Ashewa** - We're changing how Ethiopia does business!"
        ]
        
        import random
        motivation = random.choice(motivations)
        update.message.reply_text(motivation, parse_mode='Markdown')

    def run(self):
        """Start the bot"""
        logger.info("🚀 Ashewa Campaign Bot Started!")
        self.updater.start_polling()
        self.updater.idle()

def main():
    try:
        bot = AshewaCampaignBot()
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        # Keep process alive for Railway
        while True:
            time.sleep(3600)

if __name__ == '__main__':
    main()