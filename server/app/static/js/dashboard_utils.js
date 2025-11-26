// collapsable utility
function toggleSection(id) {
    const content = document.getElementById(id);
    const arrow = document.getElementById(id.replace('-content','-arrow'));
    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        arrow.textContent = '▲';
    } else {
        content.classList.add('hidden');
        arrow.textContent = '▼';
    }
}
function showStatusMessage(msg, success = true) {
    const el = document.getElementById("status-message");
    el.textContent = msg;
    el.classList.remove("hidden");
    el.classList.toggle("text-green-600", success);
    el.classList.toggle("text-red-600", !success);
    setTimeout(() => el.classList.add("hidden"), 3000); // hide after 3s
}
