import pandas as pd
import re

# Centralized category definitions for consistency between rule-based and AI categorization
CATEGORIES = {
    'Fuel': 'Gas stations, fuel purchases, petroleum',
    'Health/Pharmacy': 'Medical expenses, pharmacies, healthcare, medicines, chemist, clinic, gym, doctor, hospital',
    'Groceries': 'Food stores, supermarkets, grocery shopping, household items',
    'Dining': 'Restaurants, cafes, food delivery, takeout, bars',
    'Transport': 'Taxi, rideshare, public transport, parking, vehicle expenses',
    'Utilities': 'Electricity, water, gas bills, internet, phone bills',
    'Entertainment': 'Movies, streaming services, games, music, concerts, Netflix, drama, web series, cinema, theater, Spotify, YouTube, Amazon Prime, Disney, Hulu, Apple Music, iTunes, Steam, PlayStation, Xbox, Nintendo, media , mobile',
    'Electronics': 'Computers, laptops, smartphones, tablets, gaming consoles, audio equipment, cameras, smart home devices, accessories, cables, chargers, iPhone, Samsung, Android, MacBook, iPad, Surface, ChromeBook, PC, CPU, GPU, RAM, SSD, HDD, monitor, display, keyboard, mouse, headphone, earphone, speaker, lens, drone, smartwatch, Fitbit, Apple Watch, Garmin, router, modem, network, WiFi, Bluetooth, USB, adapter, battery, power bank, smart home, Alexa, Google Home, smart bulb, smart lock, smart thermostat, Nest, Ring, doorbell, security camera, printer, scanner, fax, projector, TV, television, smart TV, soundbar, receiver, amplifier, microphone, audio interface, mixer, DJ equipment, music production, studio equipment',
    'Shopping': 'Retail stores, clothing, general merchandise, Amazon, AliExpress, eBay, online marketplaces, e-commerce platforms, shop, store, retail, merchandise, department, mall, outlet, boutique, Shopee, Lazada, Wish, Etsy, Mercado, MercadoLibre, Flipkart, Myntra, Ajio, Nykaa, BigBasket, Grofers, Swiggy, Zomato, Uber Eats, DoorDash, Grubhub, Postmates, Caviar, Seamless, JustEat, Deliveroo, Takeaway, Foodpanda, iFood, Rappi, cornerstore, convenience, marketplace, online store, web store, digital store, e-commerce, ecommerce',
    'Education': 'Schools, courses, books, educational materials, AI tools (OpenAI, ChatGPT, Claude), programming tools, developer tools, online learning platforms, subscriptions for educational/learning purposes, skill development, professional development, certifications, tutorials, workshops, seminars, webinars, college, university, training, learning, academy, institute, fee, machine learning, ML tool, data science, tech education, software education, online learning, e-learning, digital learning',
    'Travel': 'Hotels, flights, vacation expenses, tourism',
    'Insurance': 'Insurance payments, premiums',
    'Investment': 'Stock purchases, investment accounts, savings, crypto, forex, options, futures, commodities, precious metals, financial, bank, credit, loan, mortgage',
    'Car/Service': 'Car repairs, auto service, vehicle maintenance, mechanic, garage, oil changes, brake service, tire service',
    'Recharge/Topup': ' phone topup, balance, credit recharge, prepaid/postpaid recharge, mobile balance, phone credit',
    'Misc': 'Anything that doesn\'t fit other categories'
}

# Valid categories list for validation
VALID_CATEGORIES = set(CATEGORIES.keys())

RULES = {
    r"PETROLEUM|FUEL|GAS|SHELL|EXXON|BP|CHEVRON|PETROL": "Fuel",
    r"CHEMIST|PHARMACY|CVS|WALGREENS|MEDICINE|DRUG|HEALTH|MEDICAL|CLINIC|HOSPITAL|DOCTOR|GYM": "Health/Pharmacy",
    r"STORE|MART|GROCERY|WALMART|TARGET|SUPERMARKET|MARKET|FOOD.*STORE|GROCERY.*STORE": "Groceries",
    r"RESTAURANT|CAFE|FOOD|PIZZA|BURGER|MCDONALDS|STARBUCKS|DINING|TEA.*CORNER|SWEET|DHAKA.*SWEET|CORNER|EATERY|DINER|BAKERY|FOOD.*DELIVERY|TAKEOUT|BAR|PUB|GRILL|COFFEE": "Dining",
    r"UBER|CAREEM|TAXI|RIDE|LYFT|TRANSPORT|BUS|TRAIN|RIDESHARE|CAB|METRO|SUBWAY": "Transport",
    r"ELECTRIC|UTILITY|BILL|WATER|GAS|POWER|ENERGY|SNGPL|BILLING|UTILITY.*COMPANY|POWER.*COMPANY|WATER.*COMPANY": "Utilities",
    r"NETFLIX|DRAMA|WEB.*SERIES|MOVIE|MUSIC|SHOW|STREAMING|SONG|VIDEO|AUDIO|PODCAST|ENTERTAINMENT|CINEMA|THEATER|CONCERT|GAME|GAMING|SPOTIFY|YOUTUBE|AMAZON.*PRIME|DISNEY|HULU|APPLE.*MUSIC|ITUNES|STEAM|PLAYSTATION|XBOX|NINTENDO|MEDIA|ENTERTAINMENT": "Entertainment",
    r"ELECTRONICS|COMPUTER|LAPTOP|DESKTOP|TABLET|SMARTPHONE|PHONE|MOBILE|IPHONE|SAMSUNG|ANDROID|MACBOOK|IPAD|SURFACE|CHROMEBOOK|PC|CPU|GPU|RAM|SSD|HDD|MONITOR|DISPLAY|KEYBOARD|MOUSE|HEADPHONE|EARPHONE|SPEAKER|CAMERA|LENS|DRONE|SMARTWATCH|FITBIT|APPLE.*WATCH|GARMIN|GAMING.*CONSOLE|PLAYSTATION|XBOX|NINTENDO|SWITCH|STEAM.*DECK|VR|OCULUS|META.*QUEST|ROUTER|MODEM|NETWORK|WIFI|BLUETOOTH|USB|CABLE|CHARGER|ADAPTER|BATTERY|POWER.*BANK|SMART.*HOME|ALEXA|GOOGLE.*HOME|SMART.*BULB|SMART.*LOCK|SMART.*THERMOSTAT|NEST|RING|DOORBELL|SECURITY.*CAMERA|PRINTER|SCANNER|FAX|PROJECTOR|TV|TELEVISION|SMART.*TV|SOUNDBAR|RECEIVER|AMPLIFIER|MICROPHONE|AUDIO.*INTERFACE|MIXER|DJ.*EQUIPMENT|MUSIC.*PRODUCTION|STUDIO.*EQUIPMENT|MOBILE": "Electronics",
    r"SHOP|STORE|RETAIL|CLOTHING|MERCHANDISE|DEPARTMENT|MALL|OUTLET|BOUTIQUE|AMAZON|ALIEXPRESS|ALI.*EXPRESS|EBAY|E.*BAY|SHOPEE|LAZADA|WISH|ETSY|MERCADO|MERCADOLIBRE|FLIPKART|MYNTRA|AJIO|NYKAA|BIGBASKET|GROFERS|SWIGGY|ZOMATO|UBER.*EATS|DOORDASH|GRUBHUB|POSTMATES|CAVIAR|SEAMLESS|JUSTEAT|DELIVEROO|TAKEWAY|FOODPANDA|IFOOD|RAPPI|CORNERSTORE|CONVENIENCE|MARKETPLACE|ONLINE.*STORE|WEB.*STORE|DIGITAL.*STORE|E.*COMMERCE|ECOMMERCE": "Shopping",
    r"SCHOOL|COLLEGE|UNIVERSITY|COURSE|BOOK|EDUCATION|TRAINING|LEARNING|ACADEMY|INSTITUTE|FEE|OPENAI|OPEN.*AI|CHATGPT|CLAUDE|ANTHROPIC|AI.*TOOL|AI.*SERVICE|AI.*PLATFORM|MACHINE.*LEARNING|ML.*TOOL|DATA.*SCIENCE|PROGRAMMING.*TOOL|DEVELOPER.*TOOL|CODING.*TOOL|TECH.*EDUCATION|SOFTWARE.*EDUCATION|ONLINE.*LEARNING|E.*LEARNING|DIGITAL.*LEARNING|SKILL.*DEVELOPMENT|PROFESSIONAL.*DEVELOPMENT|CERTIFICATION|TUTORIAL|WORKSHOP|SEMINAR|WEBINAR | SUBSCRIPTION": "Education",
    r"HOTEL|FLIGHT|VACATION|TOURISM|ACCOMMODATION|TRAVEL|AIRLINE|HOSTEL|RESORT": "Travel",
    r"INSURANCE|PREMIUM|COVERAGE|POLICY": "Insurance",
    r"STOCK|INVESTMENT|SAVINGS|FINANCIAL|BANK|CREDIT|LOAN|MORTGAGE|CRYPTO|FOREX|OPTIONS|FUTURES|COMMODITIES|PRECIOUS.*METALS": "Investment",
    r"CAR.*SERVICE|AUTO.*SERVICE|VEHICLE.*SERVICE|MECHANIC|GARAGE|AUTO.*REPAIR|CAR.*REPAIR|VEHICLE.*REPAIR|AUTO.*SHOP|CAR.*MAINTENANCE|VEHICLE.*MAINTENANCE|OIL.*CHANGE|BRAKE.*SERVICE|TIRE.*SERVICE|AUTO.*CENTER|CAR.*CENTER|VEHICLE.*CENTER": "Car/Service",
    r"RECHARGE|TOPUP|TOP.*UP|RECHARGE|PHONE.*RECHARGE|BALANCE.*RECHARGE|CREDIT.*RECHARGE|PREPAID.*RECHARGE|POSTPAID.*RECHARGE|MOBILE.*TOPUP|PHONE.*TOPUP|BALANCE.*TOPUP|CREDIT.*TOPUP|PREPAID.*TOPUP|POSTPAID.*TOPUP|MOBILE.*RECHARGE|CELL.*RECHARGE|SIM.*RECHARGE|DATA.*RECHARGE|INTERNET.*RECHARGE|MOBILE.*BALANCE|PHONE.*BALANCE|CELL.*BALANCE|SIM.*BALANCE|MOBILE.*CREDIT|PHONE.*CREDIT|CELL.*CREDIT|SIM.*CREDIT": "Recharge/Topup",
}

def categorize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    def match_category(desc: str):
        desc_upper = desc.upper()
        
        # Check each rule pattern
        try:
            for pattern, category in RULES.items():
                if re.search(pattern, desc_upper):
                    return category
        except Exception as e:
            print(f"Error categorizing transaction: {e}")
            return "Misc"
        
        # Additional specific checks for common cases
        if any(word in desc_upper for word in ['CHEMIST', 'PHARMACY', 'MEDICAL']):
            return "Health/Pharmacy"
        elif any(word in desc_upper for word in ['TEA', 'CORNER', 'SWEET', 'CAFE', 'RESTAURANT']):
            return "Dining"
        elif any(word in desc_upper for word in ['CAREEM', 'UBER', 'TAXI', 'RIDE']):
            return "Transport"
        elif any(word in desc_upper for word in ['OPENAI', 'OPEN AI', 'CHATGPT', 'CLAUDE', 'ANTHROPIC', 'AI TOOL', 'AI SERVICE', 'AI PLATFORM', 'MACHINE LEARNING', 'ML TOOL', 'DATA SCIENCE', 'PROGRAMMING TOOL', 'DEVELOPER TOOL', 'CODING TOOL', 'TECH EDUCATION', 'SOFTWARE EDUCATION', 'ONLINE LEARNING', 'E LEARNING', 'DIGITAL LEARNING', 'SKILL DEVELOPMENT', 'PROFESSIONAL DEVELOPMENT', 'CERTIFICATION', 'TUTORIAL', 'WORKSHOP', 'SEMINAR', 'WEBINAR']):
            return "Education"
        elif any(word in desc_upper for word in ['PODCAST', 'MUSIC', 'VIDEO', 'STREAMING']):
            return "Entertainment"
        elif any(word in desc_upper for word in ['BILLING', 'UTILITY', 'POWER', 'WATER']):
            return "Utilities"
        elif any(word in desc_upper for word in ['CAR', 'AUTO', 'VEHICLE', 'MECHANIC', 'GARAGE', 'MAINTENANCE']):
            return "Car/Service"
        elif any(word in desc_upper for word in ['RECHARGE', 'TOPUP', 'TOP-UP', 'MOBILE', 'PHONE', 'BALANCE', 'CREDIT']):
            return "Recharge/Topup"
        
        # Return None if no rule matches (for AI categorization)
        return None

    df["category"] = df["description"].apply(match_category)
    return df

def categorize_transactions_with_ai_fallback(df: pd.DataFrame) -> pd.DataFrame:
    """
    Hybrid categorization: Rule-based first, then AI-based for unmatched descriptions
    """
    # First, apply rule-based categorization
    df_categorized = categorize_transactions(df.copy())
    
    # Find rows where no rule matched (category is None)
    unmatched_mask = df_categorized["category"].isna()
    unmatched_df = df_categorized[unmatched_mask].copy()
    
    if len(unmatched_df) > 0:
        print(f"Found {len(unmatched_df)} transactions that need AI categorization")
        
        # Use AI categorization for unmatched descriptions
        try:
            import asyncio
            from .llm_client import categorize_all_with_ai
            
            # Run AI categorization for unmatched transactions
            ai_categorized_df = asyncio.run(categorize_all_with_ai(unmatched_df))
            
            # Update the original dataframe with AI-categorized results
            df_categorized.loc[unmatched_mask, "category"] = ai_categorized_df["category"]
            
            print(f"Successfully AI-categorized {len(unmatched_df)} transactions")
            
        except Exception as e:
            print(f"AI categorization failed: {e}")
            # Fallback to Misc for unmatched transactions
            df_categorized.loc[unmatched_mask, "category"] = "Misc"
    
    return df_categorized
