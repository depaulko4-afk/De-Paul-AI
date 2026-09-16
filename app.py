import streamlit as st
from google import genai
from PIL import Image

# --- FORCER LE THÈME SOMBRE DANS STREAMLIT ---
st.set_page_config(
    page_title="De Paul IA - Studio",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- CONFIGURATION DE LA CLÉ API FOURNIE ---
API_KEY = ""

try:
  client = genai.Client(api_key=API_KEY)
except Exception as e:
  client = None

# --- CUSTOM CSS (FORCAGE DU FOND NOIR ET DU TEXTE BLANC) ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117 !important;
    }
    .main {
        background-color: #0e1117 !important;
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
    }
    .stChatMessage {
        background-color: #161b22 !important;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px;
        border: 1px solid #30363d;
    }
    p, h1, h2, h3, h4, h5, h6, span, label, div {
        color: #ffffff !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: #161b22 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Détection de la langue
accept_language = st.context.headers.get("Accept-Language", "").lower()
is_french = "fr" in accept_language

if is_french:
  default_welcome = (
      "👋 Bonjour ! Je suis **De Paul IA**, votre assistant virtuel. Prêt à"
      " vous aider, analyser du texte, ou modifier et créer des images et"
      " animations. Que souhaitez-vous faire ?"
  )
  new_discussion_msg = (
      "✨ Nouvelle discussion commencée avec De Paul IA ! Comment puis-je vous"
      " aider ?"
  )
else:
  default_welcome = (
      "👋 Hello! I am **De Paul IA**, your virtual assistant. Ready to assist"
      " you, analyze text, or edit and create images and animations. What"
      " would you like to do?"
  )
  new_discussion_msg = (
      "✨ New discussion started with De Paul IA! How can I help you?"
  )

if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "assistant",
      "content": default_welcome,
  }]

# --- TOP NAVIGATION BAR ---
col_menu, col_title, col_new = st.columns([1, 3, 1], vertical_alignment="center")

with col_menu:
  if st.button("☰", help="Menu"):
    st.toast("De Paul IA Studio", icon="🤖")

with col_title:
  st.markdown(
      "<div style='text-align: center; font-weight: bold; color: white; font-"
      "size: 1.1rem;'>De Paul IA</div>",
      unsafe_allow_html=True,
  )

with col_new:
  if st.button("✏️", help="New discussion"):
    st.session_state.messages = [{
        "role": "assistant",
        "content": new_discussion_msg,
    }]
    st.rerun()

st.markdown("<hr style='margin: 5px 0 15px 0; border-color: #30363d;'>", unsafe_allow_html=True)

# --- ATTACHMENT OPTION ---
expander_label = (
    "➕ Ajouter une photo ou un fichier (Optionnel)"
    if is_french
    else "➕ Add photo or file (Optional)"
)
with st.expander(expander_label, expanded=False):
  uploader_label = (
      "Choisissez une image" if is_french else "Choose an image"
  )
  uploaded_file = st.file_uploader(uploader_label, type=["png", "jpg", "jpeg"])

uploaded_image_pil = None
if uploaded_file is not None:
  uploaded_image_pil = Image.open(uploaded_file)
  caption_text = (
      "Photo prête pour modification"
      if is_french
      else "Photo ready for modification"
  )
  st.image(
      uploaded_image_pil,
      caption=caption_text,
      width=150,
  )

# --- DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    if message.get("type") == "image":
      if message.get("input_image"):
        orig_caption = (
            "Photo originale" if is_french else "Original Photo"
        )
        st.image(message["input_image"], width=150, caption=orig_caption)
      st.image(message["content"], caption=message.get("caption"))
      download_text = (
          "📥 Télécharger l'image" if is_french else "📥 Download Image"
      )
      st.markdown(
          f"[{download_text}]({message['content']})", unsafe_allow_html=True
      )
    elif message.get("type") == "animation":
      st.image(
          message["content"],
          caption=message.get("caption"),
          use_container_width=True,
      )
      download_anim_text = (
          "📥 Télécharger l'animation" if is_french else "📥 Download Animation"
      )
      st.markdown(
          f"[{download_anim_text}]({message['content']})",
          unsafe_allow_html=True,
      )
    else:
      st.markdown(message["content"])

# --- USER INPUT ---
input_placeholder = (
    "Discutez avec De Paul IA, analysez ou demandez une image..."
    if is_french
    else "Chat with De Paul IA, analyze, or ask for an image..."
)
if prompt := st.chat_input(input_placeholder):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    if uploaded_image_pil:
      st.image(uploaded_image_pil, width=150)
    st.markdown(prompt)

  if client:
    prompt_lower = prompt.lower()
    is_video_request = any(
        kw in prompt_lower
        for kw in [
            "video",
            "tiktok",
            "reel",
            "animated",
            "animation",
            "moving",
            "animé",
            "anime",
        ]
    )
    is_image_request = (
        uploaded_image_pil is not None
        or any(
            kw in prompt_lower
            for kw in [
                "image",
                "drawing",
                "create",
                "generate",
                "photo",
                "edit",
                "modify",
                "change",
                "dessin",
                "créer",
                "generer",
                "modifier",
                "changer",
                "afro",
            ]
        )
    )

    with st.chat_message("assistant"):
      try:
        if is_video_request:
          spinner_text = (
              "🎬 De Paul IA prépare votre animation dynamique..."
              if is_french
              else "🎬 De Paul IA is crafting your dynamic animation..."
          )
          with st.spinner(spinner_text):
            enhancement_response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=(
                    "Create an engaging, cinematic, vertical 9:16 moving visual"
                    f" animation concept based on this user request: '{prompt}'."
                    " Return ONLY the final English description prompt text."
                ),
            )
            clean_prompt = enhancement_response.text.strip()
            encoded_prompt = clean_prompt.replace(" ", "%20")
            animation_url = f"https://pollinations.ai/p/{encoded_prompt}?width=540&height=960&model=flux&seed=42&nologo=true"

            st.image(
                animation_url,
                caption=prompt,
                use_container_width=True,
            )
            download_anim_text = (
                "📥 Télécharger l'animation"
                if is_french
                else "📥 Download Animation"
            )
            st.markdown(
                f"[{download_anim_text}]({animation_url})",
                unsafe_allow_html=True,
            )

            st.session_state.messages.append({
                "role": "assistant",
                "type": "animation",
                "content": animation_url,
                "caption": prompt,
            })

        elif is_image_request:
          spinner_text = (
              "📸 De Paul IA traite et modifie votre image..."
              if is_french
              else "📸 De Paul IA is processing and modifying your image..."
          )
          with st.spinner(spinner_text):
            if uploaded_image_pil:
              analysis_response = client.models.generate_content(
                  model="gemini-3.6-flash",
                  contents=[
                      uploaded_image_pil,
                      (
                          "Analyze this image and the user's editing"
                          f" instruction: '{prompt}'. Generate a detailed"
                          " professional image generation prompt in English"
                          " describing the modified version of this image."
                          " Return ONLY the prompt text."
                      ),
                  ],
              )
              clean_prompt = analysis_response.text.strip()
            else:
              enhancement_response = client.models.generate_content(
                  model="gemini-3.6-flash",
                  contents=(
                      "Create an ultra-realistic, hyper-detailed image prompt"
                      f" based on this user request: '{prompt}'. Return ONLY the"
                      " final English prompt text."
                  ),
              )
              clean_prompt = enhancement_response.text.strip()

            encoded_prompt = clean_prompt.replace(" ", "%20")
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&private=true&model=flux"

            if uploaded_image_pil:
              orig_caption = "Photo originale" if is_french else "Original Photo"
              st.image(uploaded_image_pil, width=150, caption=orig_caption)
            st.image(image_url, caption=prompt)
            download_mod_text = (
                "📥 Télécharger l'image modifiée"
                if is_french
                else "📥 Download Modified Image"
            )
            st.markdown(
                f"[{download_mod_text}]({image_url})", unsafe_allow_html=True
            )

            st.session_state.messages.append({
                "role": "assistant",
                "type": "image",
                "content": image_url,
                "caption": prompt,
                "input_image": (
                    uploaded_image_pil if uploaded_image_pil else None
                ),
            })
        else:
          spinner_text = (
              "De Paul IA réfléchit..."
              if is_french
              else "De Paul IA is thinking..."
          )
          with st.spinner(spinner_text):
            system_instruction = (
                "You are De Paul IA, an expert, friendly, and collaborative"
                " virtual assistant with deep analytical skills, precision, and"
                " clarity. Your name is De Paul IA. Structure your responses"
                " cleanly. Respond in the language used by the user."
            )

            conversation_history = ""
            for msg in st.session_state.messages[-6:]:
              role_label = "User" if msg["role"] == "user" else "Assistant"
              if "content" in msg and isinstance(msg["content"], str):
                conversation_history += f"{role_label}: {msg['content']}\n"

            full_context = (
                f"{system_instruction}\n\nDiscussion"
                f" history:\n{conversation_history}\nNew question: {prompt}"
            )

            response = client.models.generate_content(
                model="gemini-3.6-flash", contents=full_context
            )
            reply = response.text
            st.markdown(reply)

            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

      except Exception as e:
        error_msg = f"Erreur : {e}" if is_french else f"Error: {e}"
        st.error(error_msg)
  else:
    error_client_msg = (
        "⚠️ Erreur d'initialisation du client avec la clé API."
        if is_french
        else "⚠️ Error initializing client with API key."
    )
    st.error(error_client_msg)
