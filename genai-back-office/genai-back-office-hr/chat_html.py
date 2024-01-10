def get_chat_html(): 
    html = """
<link rel="stylesheet" href="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/themes/df-messenger-default.css">
<script src="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/df-messenger.js"></script>
<df-messenger
  project-id="future-backoffice-hr-assistant"
  agent-id="3d9d392f-31c3-4e10-b514-e4f1ce9d2f74"
  language-code="en">
  <df-messenger-chat-bubble
   chat-title="HR Assistant">
  </df-messenger-chat-bubble>
</df-messenger>
<style>
  df-messenger {
    z-index: 999;
    position: fixed;
    bottom: 16px;
    right: 16px;
  }
</style>
    """

    return html 