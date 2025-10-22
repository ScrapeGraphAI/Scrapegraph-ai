const $ = (sel) => document.querySelector(sel);
const jobs = new Map();

function renderJobs() {
  const tbody = $("#jobsBody");
  tbody.innerHTML = "";
  for (const [id, job] of jobs.entries()) {
    const tr = document.createElement("tr");
    const statusClass = `pill ${job.status}`;
    const fileHref = job.file_url ? job.file_url : (job.file_path ? `/download/${id}` : null);
    const fileName = job.file_path ? job.file_path.split('/').pop() : (job.file_url ? 'download.csv' : '');
    const shortId = id.substring(0, 8);
    const urlDisplay = job.url ? `${job.index}. ${job.url.substring(0, 40)}${job.url.length > 40 ? '...' : ''}` : `Job ${shortId}`;

    // Build status display with speaker count and error
    let statusDisplay = job.status;
    if (job.status === 'completed') {
      const speakerCount = job.speaker_count || 0;
      if (speakerCount > 0) {
        statusDisplay = `${job.status} (${speakerCount} speakers)`;
      } else if (job.error) {
        statusDisplay = `<span style="color: #f59e0b;">Failed to extract</span>`;
      }
    } else if (job.status === 'failed' && job.error) {
      statusDisplay = `<span title="${job.error}">failed</span>`;
    }

    // Build file column - show website name + file or error message
    let fileColumn = "–";
    if (job.error && job.speaker_count === 0) {
      fileColumn = `<span style="color: #f59e0b;" title="${job.error}">⚠️ ${job.error}</span>`;
    } else if (fileHref) {
      const websiteName = job.website_name ? `<strong>${job.website_name}</strong><br/>` : '';
      fileColumn = `${websiteName}<a class="link" href="${fileHref}">${fileName}</a>`;
    } else if (job.website_name) {
      fileColumn = `<strong>${job.website_name}</strong>`;
    }

    tr.innerHTML = `
      <td title="${job.url || id}"><code>${urlDisplay}</code></td>
      <td><span class="${statusClass}">${statusDisplay}</span></td>
      <td>${fileColumn}</td>
      <td>${job.status === 'completed' && fileHref && job.speaker_count > 0 ? `<a class="link" href="${fileHref}" download>Download File</a>` : ""}</td>
    `;
    tbody.appendChild(tr);
  }
}

async function pollStatus(id) {
  try {
    const res = await fetch(`/status/${id}`);
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    jobs.set(id, data);
    renderJobs();
    if (data.status === "completed" || data.status === "failed") return; 
  } catch (e) {
    console.error("Polling error", e);
  }
  setTimeout(() => pollStatus(id), 2000);
}

async function startJob(urls, timeout) {
  const startBtn = $("#startBtn");
  const msg = $("#startMsg");
  startBtn.disabled = true;

  try {
    // Create separate job for each URL
    msg.textContent = `Starting ${urls.length} separate jobs...`;

    const endpoint = "/scrape_sga";
    const jobPromises = urls.map(async (url, index) => {
      try {
        const payload = { urls: [url], timeout, fallback: true, prediscover: true };
        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error(`Start failed (${res.status})`);
        const data = await res.json();
        const id = data.job_id;

        // Add URL info to job for better tracking
        jobs.set(id, {
          job_id: id,
          status: data.status,
          file_path: null,
          file_url: null,
          url: url,
          index: index + 1
        });
        renderJobs();
        pollStatus(id);
        return id;
      } catch (e) {
        console.error(`Error starting job for ${url}:`, e);
        return null;
      }
    });

    const jobIds = await Promise.all(jobPromises);
    const successfulJobs = jobIds.filter(id => id !== null);

    msg.textContent = `Started ${successfulJobs.length}/${urls.length} jobs successfully`;
  } catch (e) {
    console.error(e);
    msg.textContent = `Error: ${e.message}`;
  } finally {
    startBtn.disabled = false;
  }
}

$("#startBtn").addEventListener("click", () => {
  const raw = $("#urls").value.trim();
  const timeout = parseInt($("#timeout").value || "30", 10);
  const urls = raw.split(/\n+/).map(s => s.trim()).filter(Boolean);
  if (urls.length === 0) {
    $("#startMsg").textContent = "Please enter at least one URL.";
    return;
  }
  startJob(urls, timeout);
});
