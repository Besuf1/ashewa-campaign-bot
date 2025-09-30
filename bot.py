import os
import logging
import sqlite3
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AshewaCampaignBot:
    def __init__(self):
        self.token = os.getenv('ASHEWA_BOT_TOKEN')
        logger.info(f"Bot token loaded: {'Yes' if self.token else 'No'}")
        
        if not self.token:
            logger.error("❌ ASHEWA_BOT_TOKEN not found!")
            raise ValueError("Please set ASHEWA_BOT_TOKEN environment variable")
        
        # Create Application instance (new in v20+)
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        self.init_db()
        logger.info("🤖 Ashewa Campaign Bot Initialized!")

    def init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect('ashewa_campaign.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS campaign_progress
                     (id INTEGER PRIMARY KEY, start_date TEXT, current_revenue REAL, updated_at TEXT)''')
        
        # Initialize if empty
        c.execute("SELECT * FROM campaign_progress LIMIT 1")
        if not c.fetchone():
            start_date = datetime.now().strftime("%Y-%m-%d")
            c.execute("INSERT INTO campaign_progress (start_date, current_revenue, updated_at) VALUES (?, ?, ?)",
                     (start_date, 0, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
        conn.close()

    def setup_handlers(self):
        """Setup bot command handlers"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("campaign", self.show_campaign))
        self.application.add_handler(CommandHandler("progress", self.show_progress))
        self.application.add_handler(CommandHandler("targets", self.show_targets))
        self.application.add_handler(CommandHandler("revenue", self.show_revenue))
        self.application.add_handler(CommandHandler("milestone", self.next_milestone))
        self.application.add_handler(CommandHandler("motivate", self.send_motivation))

    def get_db_connection(self):
        return sqlite3.connect('ashewa_campaign.db')

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def show_campaign(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show all marketing campaigns"""
        campaign_data = [
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
            },
            {
                'name': 'ABM Top 100 Enterprises',
                'budget': 3000000,
                'kpi': '20 enterprise + 8 govt contracts = 80M Br',
                'timeline': '60 days',
                'team': 'BD Team'
            }
        ]
        
        campaign_msg = "🎯 **ASHEWA 90-DAY MARKETING CAMPAIGNS**\n\n"
        
        for i, campaign in enumerate(campaign_data, 1):
            campaign_msg += f"**{i}. {campaign['name']}**\n"
            campaign_msg += f"   💰 Budget: {campaign['budget']:,} Br\n"
            campaign_msg += f"   🎯 KPI: {campaign['kpi']}\n"
            campaign_msg += f"   ⏰ Timeline: {campaign['timeline']}\n"
            campaign_msg += f"   👥 Team: {campaign['team']}\n\n"
        
        await update.message.reply_text(campaign_msg, parse_mode='Markdown')

    async def show_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        revenue_percent = (current_revenue / 131000000) * 100
        
        # Create progress bar
        bars = 20
        filled_bars = int((progress_percent / 100) * bars)
        empty_bars = bars - filled_bars
        progress_bar = "▓" * filled_bars + "░" * empty_bars + f" {progress_percent:.1f}%"
        
        progress_msg = f"""
⏰ **90-DAY CAMPAIGN PROGRESS**

📅 **Time Progress:** {days_passed}/90 days ({progress_percent:.1f}%)
💰 **Revenue Progress:** {current_revenue:,.0f} Br / 131,000,000 Br ({revenue_percent:.1f}%)
⏳ **Days Remaining:** {days_remaining}

{progress_bar}

**Quick Stats:**
• Daily Revenue Target: {131000000/90:,.0f} Br/day
• Revenue Needed: {131000000 - current_revenue:,.0f} Br
        """
        
        await update.message.reply_text(progress_msg, parse_mode='Markdown')
        conn.close()

    async def show_targets(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

**Account Managers:**
📋 Call 15-20 existing clients  
🎯 Weekly: 5 client upsells

**All Teams: Push for 131M Br target! 💪**
        """
        await update.message.reply_text(targets_msg, parse_mode='Markdown')

    async def show_revenue(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show revenue tracking"""
        conn = self.get_db_connection()
        c = conn.cursor()
        
        c.execute("SELECT current_revenue FROM campaign_progress LIMIT 1")
        result = c.fetchone()
        current_revenue = result[0] if result else 0
        
        revenue_msg = f"""
💰 **REVENUE TRACKING**

**Overall Target:** 131,000,000 Br
**Current Revenue:** {current_revenue:,.0f} Br
**Remaining:** {131000000 - current_revenue:,.0f} Br
**Completion:** {(current_revenue/131000000)*100:.1f}%

**Daily Target:** {131000000/90:,.0f} Br/day

*Keep pushing! Every deal counts!* 🚀
        """
        
        await update.message.reply_text(revenue_msg, parse_mode='Markdown')
        conn.close()

    async def next_milestone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        await update.message.reply_text(milestone_msg, parse_mode='Markdown')
        conn.close()

    async def send_motivation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text(motivation, parse_mode='Markdown')

    def run(self):
        """Start the bot"""
        logger.info("🚀 Starting Ashewa Campaign Bot...")
        self.application.run_polling()
        logger.info("✅ Bot is now running and polling!")

def main():
    logger.info("=== ASHEWA BOT STARTING ===")
    try:
        bot = AshewaCampaignBot()
        bot.run()
    except Exception as e:
        logger.error(f"❌ Bot failed to start: {e}")
        # Keep process alive for Railway
        import time
        while True:
            time.sleep(60)

if __name__ == '__main__':
    main()
