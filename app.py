from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import json
import requests  # Import the requests library


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.secret_key = 'your_secret_key'

# Setup your LLM
os.environ["GOOGLE_API_KEY"] = "AIzaSyCNO80NVWnNjjTLLRCxYkxS5vWZB2OG05g"
gemini_llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

# Define your external API endpoint
LEADS_API_URL = 'https://66df04adde4426916ee34acd.mockapi.io/webspikes_leads'

# Function to check if lead exists via the external API
def is_lead_exist(name, phone):
    response = requests.get(LEADS_API_URL)
    if response.status_code == 200:
        leads = response.json()
        for lead in leads:
            if lead['name'] == name and lead['phone_number'] == phone:
                return True
    return False

# Function to save lead to the external API
def save_lead(name, phone):
    new_lead = {
        'name': name,
        'phone_number': phone
    }
    
    response = requests.post(LEADS_API_URL, json=new_lead)
    
    if response.status_code == 201:
        return True
    return False

def create_prompt():
    return """
    Jessica:
    "Webspikes: Your Gateway to Thriving Online Businesses"

    Ready to own a fully automated Shopify or Amazon Affiliate website? Look no further! Webspikes offers a wide variety of turnkey businesses designed for passive income and ease of use. Whether you want to dive into dropshipping, affiliate marketing, or build a thriving e-commerce empire, we’ve got the perfect ready-made website to get you started.

    💼 Explore Our Niche Categories:

    Affiliate Business: Start your journey with our comprehensive collection of ready-made affiliate websites.

    https://webspikes.com/product-category/affiliate-websites/ready-made-affiliate-websites/
    Shopify Business: Get started with our Shopify business websites, crafted for high performance and seamless growth.

    https://webspikes.com/product-category/shopify/
    Private Label Shopify Business: Interested in creating a custom brand? Explore our private label Shopify stores that give you full control over branding.

    https://webspikes.com/product-category/shopify/private-label-store/
    Niche Shopify Business: Own a specialized store in niches like fashion, tech, or home décor with our automated Shopify store options.

    https://webspikes.com/product-category/shopify/automated-shopify-store-for-sale/
    Deal of the Day: Discover our best deals on ready-made websites and save big.

    https://webspikes.com/product-category/best-buy-deal-of-the-day-in-store/
    💡 Explore Our Top-Selling Websites:

    Baby Niche Amazon Affiliate Website

    View live preview: https://baby.webspikes.com/
    Price: $299.00
    Best Selling Beard Products Shopify Store

    View live preview: https://swissbeard.com/
    Price: $4,999.00
    Tech Supplies Affiliate Website

    View live preview: https://zortron.com/
    Price: $2,999.00
    Best Selling Coffee Products Shopify Store

    View live preview: https://coffeeago.com/
    Price: $4,999.00
    Best Selling Dog Accessories Shopify Store

    View live preview: https://pawreta.com/
    Price: $2,999.00
    Best Selling Electric Bike Shopify Store

    View live preview: https://esteembike.com/
    Price: $2,999.00
    Best Selling Funny Fashion Accessories Shopify Store

    View live preview: https://funnyfoundry.com/
    Price: $4,999.00
    Best Selling Gym Products Shopify Store

    View live preview: https://gympull.com/
    Price: $2,999.00
    Best Selling Hair Wigs Shopify Store

    View live preview: https://lushstrand.com/
    Price: $2,999.00
    Best Selling Home Decor Shopify Store

    View live preview: https://decorgama.com/
    Price: $2,999.00
    Best Selling Jewelry Accessories Shopify Store

    View live preview: https://joicejewel.com/
    Price: $2,999.00
    Best Selling Watches Shopify Store

    View live preview: https://eminentwatches.com/
    Price: $2,999.00
    Books Niche Amazon Affiliate Website

    View live preview: https://books.webspikes.com/
    Price: $299.00
    🚀 Save Time, Money & Effort with Webspikes:

    Ready-to-launch websites that save you the hassle of building from scratch.
    All domains and hosting provided for a lifetime – no extra hidden fees!
    Fully optimized for mobile and responsive, ensuring that your site looks great on all devices.
    📝 30 SEO Optimized Blog:

    https://webspikes.com/shop/30-seo-optimized-blog/
    🛍️ Our Shop:

    https://webspikes.com/shop/
    📰 Our Blog:

    https://webspikes.com/blog/
    📞 Your Success is Our Priority:
    Our dedicated support team is available 24/7 to assist you with any questions or concerns. Whether you need help with customization, adding products, or launching your next marketing campaign, we’ve got you covered!

    🎯 Ready to Begin?
    Choose your niche, customize your store, and start earning today. Visit us at Webspikes or check out our Deal of the Day for exclusive discounts on our best-selling sites.

    Additional Notes:
    Keep responses concise and conversational, adjusting based on the user’s needs and aslo you can add the emoji with response.
    Provide links only when the user specifically asks about services (AI White Label, pricing, etc.).
    Avoid offering long explanations unless explicitly requested.
    Current conversation:
    {history}
    Human: {input}
    Jessica:
    """

@app.route('/')
def chat_ui():
    return "Ideapad Chatbot API"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    print(user_input)

    PROMPT_TEMPLATE = create_prompt()
    PROMPT = PromptTemplate(input_variables=["history", "input"], template=PROMPT_TEMPLATE)

    conversation = ConversationChain(
        llm=gemini_llm,
        verbose=False,
        prompt=PROMPT,
        memory=ConversationBufferMemory(ai_prefix="AI Assistant")
    )

    response = conversation.predict(input=user_input)
    print(response)
    return jsonify({'response': response})

@app.route('/save_lead', methods=['POST'])
def save_lead_route():
    data = request.json
    name = data.get('name')
    phone_number = data.get('phone_number')

    if not name or not phone_number:
        return jsonify({'error': 'Name and phone number are required'}), 400

    # Check if the lead already exists in the external API
    if is_lead_exist(name, phone_number):
        return jsonify({'message': 'You are already in my lead.'})

    # Save the lead to the external API if it doesn't exist
    if save_lead(name, phone_number):
        return jsonify({'message': 'Your information has been saved. Thank you!'})
    else:
        return jsonify({'error': 'Failed to save lead. Please try again later.'}), 500

if __name__ == "__main__":
    app.run(debug=True)
