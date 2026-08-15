async function checkApiHealth() {
    const statusElement = document.getElementById("api-status");

    if (!statusElement) {
        return;
    }

    try {
        const response = await fetch("/api/health");

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (data.status === "ok") {
            statusElement.textContent = "Garden connection: alive";
            statusElement.classList.add("ok");
            return;
        }

        throw new Error("Unexpected health response");
    } catch (error) {
        console.error("Health check failed:", error);
        statusElement.textContent = "Garden connection: unavailable";
        statusElement.classList.add("error");
    }
}

checkApiHealth();
