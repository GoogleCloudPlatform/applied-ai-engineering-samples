# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# noqa: E501

magi_result_carousel = """
    <ul class="magi-search-results">
        <li>
            <a href="/blog/1">
                <h4>Unleashing the Techie Within: A Journey to FIRE</h4>
                <p>The heart of Silicon Valley, where innovation pulsates like an electric current, a revolution is brewing – a revolution of liberation, not from technology, but from the traditional shackles of work. Tech employees, the pioneers of the digital age, are embracing the FIRE movement (Financial Independence, Retire Early), seeking financial emancipation and the freedom to pursue their passions.</p>
            </a>
        </li>
        <li>
            <a href="/blog/2">
                <h4>Navigating the Investment Jungle: A Beginner's Guide to ETFs</h4>
                <p>Imagine yourself wandering through a dense rainforest, teeming with exotic flora and fauna. The air is thick with the scent of unfamiliar plants, and the sounds of unseen creatures echo through the dense canopy overhead. It's a world of bewildering complexity, yet also one brimming with potential for discovery.
            </p>
            </a>
        </li>
    </ul>
    """

magi_follow_up_controls = """
    <div class="magi-actions-container" >
        <div class="search-bar" style="background-color: white;" >
            <div style="width:100%;">
                <input type="text" id="prompt-follow-up" name="thequery" title="Search" type="search" value="" placeholder="Ask ..."
                    aria-label="Search"
                    hx-post="/web/magi-follow?conversation_name={{conversation_name}}"
                    hx-indicator="#loading-initial"
                    hx-include="#prompt-follow-up"
                    hx-trigger="keydown[keyCode==13] from:input"
                    hx-target="#magi-container-target"
                    style="width: 100%;" />
            </div>
        </div>
        <div class="magi-buttons">
            <button type="submit" hx-post="/web/magi-follow?conversation_name={{conversation_name}}" 
                hx-indicator="#loading-initial"
                hx-include="#prompt-follow-up"
                hx-target="#magi-container-target">
                <span class="google-symbols"> astrophotography_mode </span>
                Ask a follow up
            </button>
        </div>
    </div>

    """


magi_carousel_conversation = """
    <div class="magi-conversation-container">

        <style>
        /* Style the chat container */
        .chat-container {
        width: 500px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        }

        /* Style the chat message */
        .chat-message {
        margin: 10px 0;
        padding: 15px;
        border-radius: 5px;
        background-color: #f2f2f2;
        }

        /* Style the chat message for the recipient */
        .chat-message.recipient {
        align-self: flex-start;
        background-color: #e6e6ff;
        }

        /* Style the chat message for the sender */
        .chat-message.sender {
        align-self: flex-end;
        background-color: #f2f2f2;
        }

        /* Style the chat message content */
        .chat-message-content {
        font-size: 16px;
        }
        </style>

        <div class="chat-container">
        <div class="chat-message sender">
        <div class="chat-message-content">{}</div>
        </div>
        <div class="chat-message recipient">
        <div class="chat-message-content">{}</div>
        </div>
"""
