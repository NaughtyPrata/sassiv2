// main.js for chat-ui.html
const API_BASE = 'http://localhost:7878';
let conversationId = null;
let messageCount = 0;

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const resetButton = document.getElementById('resetButton');
const statusBar = document.getElementById('status-bar');
const agentStatusIndicator = document.getElementById('agent-status-indicator');
const angerMeterBar = document.getElementById('anger-meter-bar');
const angerMeterPoints = document.getElementById('anger-meter-points');
const intensityIndicator = document.getElementById('intensity-indicator');
const intensityLabel = document.getElementById('intensity-label');
const trajectoryIndicator = document.getElementById('trajectory-indicator');
const triggersIndicator = document.getElementById('triggers-indicator');
const aiInsightsState = document.getElementById('ai-insights-state');
const aiInsightsStrategy = document.getElementById('ai-insights-strategy');

// Focus input on load
if (messageInput) messageInput.focus();

// Send message on button click or enter
if (sendButton && messageInput) {
  sendButton.addEventListener('click', () => {
    const message = messageInput.value.trim();
    if (message) sendMessage(message);
  });
  messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const message = messageInput.value.trim();
      if (message) sendMessage(message);
    }
  });
}

// Reset conversation
if (resetButton) {
  resetButton.addEventListener('click', async () => {
    if (confirm('Are you sure you want to reset the conversation and anger meter?')) {
      await resetConversation();
    }
  });
}

async function sendMessage(message) {
  setInputState(false);
  messageInput.value = '';
  addUserMessage(message);
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, conversation_id: conversationId })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    const data = await response.json();
    if (!conversationId) conversationId = data.conversation_id;
    addBotMessage(data.response, data.agent_type, data.timestamp);
    updateIndicators(data);
  } catch (error) {
    addErrorMessage(`Error: ${error.message}. Make sure the server is running on port 7878.`);
  } finally {
    setInputState(true);
    messageInput.focus();
  }
}

function addUserMessage(content) {
  messageCount++;
  const div = document.createElement('div');
  div.className = 'flex flex-col items-end';
  div.innerHTML = `
    <div class="text-xs text-gray-400 mb-1">You • ${new Date().toLocaleTimeString()}</div>
    <div class="inline-block bg-blue-100 rounded-xl px-4 py-3 shadow-sm">${escapeHtml(content)}</div>
  `;
  chatMessages.appendChild(div);
  scrollToBottom();
}

function addBotMessage(content, agentType, timestamp) {
  // Highlight <t>...</t> meta messages with a muted color
  let html = '';
  const tRegex = /<t>([\s\S]*?)<\/t>/g;
  let lastIndex = 0;
  let match;
  while ((match = tRegex.exec(content)) !== null) {
    // Add text before <t>
    if (match.index > lastIndex) {
      html += escapeHtml(content.slice(lastIndex, match.index));
    }
    // Add <t>...</t> with special class
    html += `<span class="bot-meta-message">${escapeHtml(match[1])}</span>`;
    lastIndex = tRegex.lastIndex;
  }
  // Add any remaining text after last <t>
  if (lastIndex < content.length) {
    html += escapeHtml(content.slice(lastIndex));
  }
  if (!html) html = escapeHtml(content);
  const div = document.createElement('div');
  div.innerHTML = `
    <div class="text-xs text-gray-400 mb-1">ESE (${agentType || 'normal'}) • ${timestamp ? new Date(timestamp).toLocaleTimeString() : 'now'}</div>
    <div class="inline-block bg-gray-100 rounded-xl px-4 py-3 shadow-sm">${html}</div>
  `;
  chatMessages.appendChild(div);
  scrollToBottom();
}

function addErrorMessage(message) {
  const div = document.createElement('div');
  div.className = 'text-xs text-red-600 mb-2';
  div.textContent = message;
  chatMessages.appendChild(div);
  scrollToBottom();
}

function setInputState(enabled) {
  if (messageInput) messageInput.disabled = !enabled;
  if (sendButton) sendButton.disabled = !enabled;
  if (resetButton) resetButton.disabled = !enabled;
  if (sendButton) sendButton.textContent = enabled ? 'Send' : 'Sending...';
}

async function resetConversation() {
  setInputState(false);
  try {
    const response = await fetch(`${API_BASE}/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    const data = await response.json();
    chatMessages.innerHTML = '';
    conversationId = null;
    messageCount = 0;
    addBotMessage(`✅ ${data.message} - Anger meter reset to ${data.anger_points || 0} points`, 'system', new Date().toISOString());
    resetIndicators();
  } catch (error) {
    addErrorMessage(`Reset failed: ${error.message}`);
  } finally {
    setInputState(true);
    messageInput.focus();
  }
}

function updateIndicators(data) {
  // Status bar
  if (statusBar && data.agent_type && data.sentiment_analysis && data.sentiment_analysis.intensity !== undefined) {
    statusBar.textContent = `Status: Online | Current: ${capitalize(data.agent_type)} | Intensity: ${data.sentiment_analysis.intensity}/1.0`;
  }
  // Agent status
  if (agentStatusIndicator && data.agent_type) {
    const emoji = agentEmoji(data.agent_type);
    agentStatusIndicator.innerHTML = `${emoji} <span class="font-bold">${data.agent_type.toUpperCase()}</span>`;
  }
  // Anger meter
  if (angerMeterBar && data.orchestrator_decision && data.orchestrator_decision.anger_meter) {
    const anger = data.orchestrator_decision.anger_meter;
    const percent = Math.round((anger.anger_points / anger.max_points) * 100);
    angerMeterBar.style.width = percent + '%';
    angerMeterPoints.textContent = `${anger.anger_points}/${anger.max_points} pts`;
  }
  // Intensity
  if (intensityIndicator && data.sentiment_analysis && data.sentiment_analysis.intensity !== undefined) {
    intensityIndicator.textContent = `${data.sentiment_analysis.intensity}/1.0`;
    intensityLabel.textContent = intensityLabelText(data.sentiment_analysis.intensity);
  }
  // Trajectory
  if (trajectoryIndicator && data.orchestrator_insights && data.orchestrator_insights.conversation_trajectory) {
    trajectoryIndicator.textContent = data.orchestrator_insights.conversation_trajectory;
  }
  // Triggers
  if (triggersIndicator && data.orchestrator_insights && data.orchestrator_insights.detected_triggers) {
    triggersIndicator.innerHTML = '';
    data.orchestrator_insights.detected_triggers.forEach(trigger => {
      const span = document.createElement('span');
      span.className = 'bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded';
      span.textContent = `'${trigger}'`;
      triggersIndicator.appendChild(span);
    });
  }
  // AI Insights
  if (aiInsightsState && data.orchestrator_insights && data.orchestrator_insights.state_transition) {
    aiInsightsState.innerHTML = `<strong>State Transition:</strong> ${data.orchestrator_insights.state_transition}`;
  }
  if (aiInsightsStrategy && data.orchestrator_insights && data.orchestrator_insights.orchestrator_suggestion) {
    aiInsightsStrategy.innerHTML = `<strong>Strategy:</strong> ${data.orchestrator_insights.orchestrator_suggestion}`;
  }
  // Agent indicator highlight
  highlightActiveAgent(data.agent_type);
}

function resetIndicators() {
  if (statusBar) statusBar.textContent = 'Status: Online | Current: Normal | Intensity: 0.0/1.0';
  if (agentStatusIndicator) agentStatusIndicator.innerHTML = '🙂 <span class="font-bold">NORMAL</span>';
  if (angerMeterBar) angerMeterBar.style.width = '0%';
  if (angerMeterPoints) angerMeterPoints.textContent = '0/100 pts';
  if (intensityIndicator) intensityIndicator.textContent = '0.0/1.0';
  if (intensityLabel) intensityLabel.textContent = 'No emotion';
  if (trajectoryIndicator) trajectoryIndicator.textContent = '';
  if (triggersIndicator) triggersIndicator.innerHTML = '';
  if (aiInsightsState) aiInsightsState.innerHTML = '<strong>State Transition:</strong> None';
  if (aiInsightsStrategy) aiInsightsStrategy.innerHTML = '<strong>Strategy:</strong> None';
  highlightActiveAgent('normal');
}

function highlightActiveAgent(agentType) {
  const all = document.querySelectorAll('.agent-list-item');
  all.forEach(li => li.classList.remove('active-agent', 'bg-blue-200'));
  if (agentType) {
    // Normalize agentType to match HTML IDs
    let normalized = agentType.toLowerCase().replace(/_agent$/, '');
    // Map short names to full IDs if needed
    const map = {
      normal: 'agent-normal',
      pleased: 'agent-happy-level1-pleased',
      cheerful: 'agent-happy-level2-cheerful',
      ecstatic: 'agent-happy-level3-ecstatic',
      melancholy: 'agent-sad-level1-melancholy',
      sorrowful: 'agent-sad-level2-sorrowful',
      depressed: 'agent-sad-level3-depressed',
      irritated: 'agent-angry-level1-irritated',
      agitated: 'agent-angry-level2-agitated',
      enraged: 'agent-angry-level3-enraged',
      'happy_level1_pleased': 'agent-happy-level1-pleased',
      'happy_level2_cheerful': 'agent-happy-level2-cheerful',
      'happy_level3_ecstatic': 'agent-happy-level3-ecstatic',
      'sad_level1_melancholy': 'agent-sad-level1-melancholy',
      'sad_level2_sorrowful': 'agent-sad-level2-sorrowful',
      'sad_level3_depressed': 'agent-sad-level3-depressed',
      'angry_level1_irritated': 'agent-angry-level1-irritated',
      'angry_level2_agitated': 'agent-angry-level2-agitated',
      'angry_level3_enraged': 'agent-angry-level3-enraged',
    };
    let id = map[normalized] || `agent-${normalized.replace(/_/g, '-')}`;
    const el = document.getElementById(id);
    if (el) el.classList.add('active-agent', 'bg-blue-200');
  }
}

function agentEmoji(agentType) {
  if (!agentType) return '🙂';
  const map = {
    normal: '🙂',
    'happy-level1-pleased': '😊',
    'happy-level2-cheerful': '😄',
    'happy-level3-ecstatic': '🤩',
    'sad-level1-melancholy': '😔',
    'sad-level2-sorrowful': '😢',
    'sad-level3-depressed': '😭',
    'angry-level1-irritated': '😠',
    'angry-level2-agitated': '😡',
    'angry-level3-enraged': '🤬'
  };
  return map[agentType.toLowerCase()] || '🙂';
}

function intensityLabelText(intensity) {
  if (intensity >= 0.8) return 'Very strong emotion';
  if (intensity >= 0.5) return 'Moderate emotion';
  if (intensity > 0.2) return 'Mild emotion';
  return 'No emotion';
}

function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Test server connection on load
async function testConnection() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error('Server responded with error');
  } catch (error) {
    addErrorMessage('⚠️ Cannot connect to server. Make sure to run ./startup.sh first!');
  }
}
testConnection(); 