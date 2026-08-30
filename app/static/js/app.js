/**
 * Fandango Investigation Editorial Interactive Experience
 */

const API_BASE = "";
let chartInstances = {};
let allMoviesData = [];
let activeFilter = "all";
let currentTheme = localStorage.getItem("fandango_editorial_theme") || "light";

document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

async function initApp() {
  initTheme();
  initTabs();
  initGlitchSimulator();
  initScaleConverter();
  initTicketImpactSimulator();
  initFilmExplorerEvents();
  initSQLWorkbenchEvents();
  initExportButton();

  try {
    await Promise.all([
      loadOverview(),
      loadMoviesData(),
      loadDiscrepancies(),
      loadPlatforms(),
      loadTemporal(),
      loadStats(),
      loadSQLPresets(),
    ]);
  } catch (err) {
    console.error("Init Error:", err);
  }
}

// 1. Theme Management
function initTheme() {
  document.documentElement.setAttribute("data-theme", currentTheme);
  const toggleBtn = document.getElementById("themeToggle");
  if (toggleBtn) {
    toggleBtn.innerHTML = currentTheme === "dark" ? "☀️ Light Theme" : "🌙 Dark Theme";
    toggleBtn.addEventListener("click", () => {
      currentTheme = currentTheme === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", currentTheme);
      localStorage.setItem("fandango_editorial_theme", currentTheme);
      toggleBtn.innerHTML = currentTheme === "dark" ? "☀️ Light Theme" : "🌙 Dark Theme";
      
      Object.values(chartInstances).forEach(chart => {
        if (chart && chart.update) chart.update();
      });
    });
  }
}

// 2. Tab Navigation
function initTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      tab.classList.add("active");
      const target = document.getElementById(tab.getAttribute("data-tab"));
      if (target) target.classList.add("active");
      window.dispatchEvent(new Event('resize'));
    });
  });
}

// 3. Glitch Simulator (Top Interactive Slider)
function initGlitchSimulator() {
  const slider = document.getElementById("glitchSlider");
  const trueValEl = document.getElementById("simTrueRating");
  const mathRoundEl = document.getElementById("simMathRound");
  const fandangoRoundEl = document.getElementById("simFandangoRound");
  const glitchDeltaEl = document.getElementById("simGlitchDelta");
  const simNoteEl = document.getElementById("simNote");

  function updateSimulator(val) {
    const trueScore = parseFloat(val);
    if (trueValEl) trueValEl.textContent = trueScore.toFixed(1);

    const mathRound = Math.round(trueScore * 2) / 2;
    if (mathRoundEl) mathRoundEl.textContent = `${mathRound.toFixed(1)} ★`;

    const intPart = Math.floor(trueScore);
    const frac = Math.round((trueScore - intPart) * 10) / 10;
    let fandangoRound = intPart;
    if (frac === 0.0) {
      fandangoRound = intPart;
    } else if (frac <= 0.5) {
      fandangoRound = intPart + 0.5;
    } else {
      fandangoRound = intPart + 1.0;
    }

    if (fandangoRoundEl) fandangoRoundEl.textContent = `${fandangoRound.toFixed(1)} ★`;

    const delta = (fandangoRound - mathRound).toFixed(1);
    if (glitchDeltaEl) {
      if (delta > 0) {
        glitchDeltaEl.innerHTML = `<span style="color: var(--fte-crimson);">+${delta} ★ Inflation</span>`;
      } else {
        glitchDeltaEl.innerHTML = `<span style="color: var(--fte-green);">0.0 ★ Normal</span>`;
      }
    }

    if (simNoteEl) {
      if (frac >= 0.1 && frac < 0.25) {
        simNoteEl.textContent = `Glitch Active: A rating of ${trueScore.toFixed(1)} is mathematically 4.0★, but Fandango pushed it up to 4.5★!`;
      } else if (frac >= 0.6 && frac < 0.75) {
        simNoteEl.textContent = `Glitch Active: A rating of ${trueScore.toFixed(1)} is mathematically 4.5★, but Fandango pushed it up to 5.0★!`;
      } else {
        simNoteEl.textContent = `Standard half-round interval point.`;
      }
    }
  }

  slider?.addEventListener("input", (e) => updateSimulator(e.target.value));
  updateSimulator(4.1);
}

// 4. Safe Fetch Helper
async function safeFetchJson(endpoint, embeddedKey) {
  try {
    if (window.location.protocol !== "file:") {
      const res = await fetch(endpoint);
      if (res.ok) return await res.json();
    }
  } catch (e) {
    // fallback to embedded
  }
  if (typeof EMBEDDED_DATA !== "undefined" && EMBEDDED_DATA[embeddedKey]) {
    return EMBEDDED_DATA[embeddedKey];
  }
  return null;
}

// 5. Overview & Disparities
async function loadOverview() {
  try {
    const data = await safeFetchJson(`${API_BASE}/api/overview`, 'overview');
    if (!data) return;

    document.getElementById("kpiTotalSample").textContent = data.total_2015_movies;
    document.getElementById("kpiDisplayedAvg").textContent = Number(data.avg_displayed_stars_2015).toFixed(2);
    document.getElementById("kpiActualAvg").textContent = Number(data.avg_actual_rating_2015).toFixed(2);
    document.getElementById("kpiInflationDelta").textContent = `+${Number(data.avg_inflation_delta).toFixed(2)} ★`;
    document.getElementById("kpiRoundedUpRate").textContent = `${data.rounded_up_pct_2015}%`;
    document.getElementById("kpiPostArticleAvg").textContent = Number(data.avg_displayed_stars_2016_17).toFixed(2);
    document.getElementById("kpiPostShift").textContent = `${Number(data.temporal_change).toFixed(2)} ★`;

    if (data.top_disparities) {
      renderDisparityGallery(data.top_disparities);
    }
  } catch (err) {
    console.error("Overview error:", err);
  }
}

function renderDisparityGallery(disparities) {
  const container = document.getElementById("disparityGrid");
  if (!container) return;

  container.innerHTML = disparities.map(d => `
    <div class="disparity-card">
      <div class="disparity-title" title="${d.film}">${d.film}</div>
      <div class="disparity-comparison-bar">
        <div class="platform-score-box">
          <div class="platform-score-label">Rotten Tomatoes</div>
          <div class="platform-score-num" style="color: var(--color-rt);">${d.rt_raw}% <span style="font-size: 0.8rem;">(${d.rt_norm.toFixed(1)}★)</span></div>
        </div>
        <div style="font-size: 1.5rem; font-weight: 800; color: var(--text-muted);">vs</div>
        <div class="platform-score-box">
          <div class="platform-score-label">Fandango Displayed</div>
          <div class="platform-score-num" style="color: var(--fte-crimson);">${d.fandango_stars.toFixed(1)} ★</div>
        </div>
      </div>
      <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--text-dim);">
        <span>True HTML Rating: <strong>${d.fandango_actual.toFixed(2)}</strong></span>
        <span class="diff-badge" style="background: rgba(255, 39, 0, 0.1); color: var(--fte-crimson);">+${d.gap.toFixed(2)} ★ Gap</span>
      </div>
    </div>
  `).join("");
}

// 6. Movies Data & Parity Scatter Plot
async function loadMoviesData() {
  try {
    const data = await safeFetchJson(`${API_BASE}/api/movies?limit=200`, 'movies');
    if (!data) return;
    allMoviesData = data;

    renderFilteredFilms();
    renderParityScatterPlot(allMoviesData);
    renderWallOfInflation(allMoviesData);

    if (allMoviesData.length > 0) {
      updateSpotlight(allMoviesData[0]);
    }
  } catch (err) {
    console.error("Movies data error:", err);
  }
}

function updateSpotlight(film) {
  if (!film) return;
  document.getElementById("spotTitle").textContent = film.film;
  document.getElementById("spotStars").textContent = `${Number(film.fandango_stars).toFixed(1)} ★`;
  document.getElementById("spotActual").textContent = `${Number(film.fandango_actual).toFixed(2)} / 5.0`;
  document.getElementById("spotDiff").textContent = `+${Number(film.discrepancy).toFixed(2)} Stars`;
  document.getElementById("spotRT").textContent = `${Number(film.rt_norm).toFixed(2)} ★`;
  document.getElementById("spotMeta").textContent = `${Number(film.metacritic_norm).toFixed(2)} ★`;
  document.getElementById("spotIMDB").textContent = `${Number(film.imdb_norm).toFixed(2)} ★`;
  document.getElementById("spotVotes").textContent = Number(film.votes).toLocaleString();
}

function renderParityScatterPlot(movies) {
  const ctx = document.getElementById("parityScatterChart")?.getContext("2d");
  if (!ctx || typeof Chart === "undefined") return;

  const points = movies.map(m => ({
    x: m.fandango_actual,
    y: m.fandango_stars,
    film: m.film,
    diff: m.discrepancy,
    rt: m.rt_norm,
    meta: m.metacritic_norm,
    imdb: m.imdb_norm,
    votes: m.votes,
  }));

  const parityLine = [
    { x: 2.5, y: 2.5 },
    { x: 5.0, y: 5.0 }
  ];

  if (chartInstances.parity) chartInstances.parity.destroy();

  chartInstances.parity = new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Zero Inflation Line (Displayed = True)",
          data: parityLine,
          type: "line",
          borderColor: "rgba(148, 163, 184, 0.5)",
          borderDash: [5, 5],
          borderWidth: 2,
          pointRadius: 0,
          fill: false,
        },
        {
          label: "146 Theatrical Releases (2015)",
          data: points,
          pointRadius: (ctx) => {
            const diff = ctx.raw?.diff || 0;
            return diff >= 0.5 ? 7 : (diff >= 0.4 ? 6 : 4.5);
          },
          pointHoverRadius: 9,
          pointBackgroundColor: (ctx) => {
            const diff = ctx.raw?.diff || 0;
            if (diff >= 0.5) return "#ff2700";
            if (diff >= 0.4) return "#f59e0b";
            if (diff >= 0.2) return "#fbbf24";
            return "#008fd5";
          },
          pointBorderColor: "#ffffff",
          pointBorderWidth: 1.5,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      onClick: (e, elements) => {
        if (elements.length > 0) {
          const index = elements[0].index;
          const film = points[index];
          if (film) updateSpotlight(film);
        }
      },
      plugins: {
        legend: {
          labels: {
            color: currentTheme === "dark" ? "#cbd5e1" : "#334155",
            font: { family: "'Plus Jakarta Sans', sans-serif", size: 11, weight: "600" }
          }
        },
        tooltip: {
          backgroundColor: currentTheme === "dark" ? "#111726" : "#ffffff",
          titleColor: currentTheme === "dark" ? "#ffffff" : "#0f172a",
          titleFont: { family: "'Newsreader', serif", weight: "700", size: 14 },
          bodyColor: currentTheme === "dark" ? "#cbd5e1" : "#475569",
          bodyFont: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
          padding: 12,
          borderColor: currentTheme === "dark" ? "rgba(255,255,255,0.15)" : "#cbd5e1",
          borderWidth: 1,
          displayColors: false,
          callbacks: {
            title: (items) => items[0].raw.film || "Zero Inflation Line",
            label: (item) => {
              const r = item.raw;
              if (!r.film) return "Parity Reference (Y = X)";
              return [
                `Displayed: ${r.y.toFixed(1)} ★  |  True HTML: ${r.x.toFixed(2)}`,
                `Inflation Delta: +${r.diff.toFixed(2)} Stars`,
                `RT: ${r.rt.toFixed(2)} ★ | Metacritic: ${r.meta.toFixed(2)} ★ | IMDB: ${r.imdb.toFixed(2)} ★`,
                `Votes: ${r.votes.toLocaleString()}`
              ];
            }
          }
        }
      },
      scales: {
        x: {
          min: 2.5,
          max: 5.0,
          title: {
            display: true,
            text: "True Underlying HTML Rating (Unrounded)",
            color: currentTheme === "dark" ? "#94a3b8" : "#475569",
            font: { weight: "700", size: 11 }
          },
          grid: { color: currentTheme === "dark" ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.06)" }
        },
        y: {
          min: 2.5,
          max: 5.2,
          title: {
            display: true,
            text: "Displayed Stars on Fandango",
            color: currentTheme === "dark" ? "#94a3b8" : "#475569",
            font: { weight: "700", size: 11 }
          },
          grid: { color: currentTheme === "dark" ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.06)" }
        }
      }
    }
  });
}

function renderWallOfInflation(movies) {
  const container = document.getElementById("wallGrid");
  if (!container) return;

  const topInflated = movies.filter(m => m.discrepancy >= 0.5).slice(0, 8);

  container.innerHTML = topInflated.map(m => `
    <div class="wall-card" onclick="updateSpotlightByName('${m.film.replace(/'/g, "\\'")}')">
      <div class="wall-card-title" title="${m.film}">${m.film}</div>
      <div class="wall-stars-row">
        <span class="star-rating-display">${getVisualStars(m.fandango_stars)}</span>
        <span class="diff-badge">+${Number(m.discrepancy).toFixed(2)} ★</span>
      </div>
      <div class="wall-meta-row">
        <span>True: ${Number(m.fandango_actual).toFixed(2)} / 5.0</span>
        <span>RT: ${Number(m.rt_norm).toFixed(1)} ★</span>
      </div>
    </div>
  `).join("");
}

window.updateSpotlightByName = (name) => {
  const found = allMoviesData.find(m => m.film === name);
  if (found) {
    updateSpotlight(found);
    window.scrollTo({ top: document.querySelector('.split-plot-wrapper')?.offsetTop - 80 || 0, behavior: 'smooth' });
  }
};

function getVisualStars(rating) {
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.4 ? 1 : 0;
  const empty = 5 - full - half;
  return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(empty);
}

// 7. Discrepancy Breakdown
async function loadDiscrepancies() {
  try {
    const data = await safeFetchJson(`${API_BASE}/api/discrepancies`, 'discrepancies');
    if (!data) return;

    const labels = data.breakdown.map(item => `+${item.difference.toFixed(1)} ★`);
    const counts = data.breakdown.map(item => item.count);

    const ctx = document.getElementById("roundingStepChart")?.getContext("2d");
    if (ctx && typeof Chart !== "undefined") {
      if (chartInstances.rounding) chartInstances.rounding.destroy();

      chartInstances.rounding = new Chart(ctx, {
        type: "bar",
        data: {
          labels: labels,
          datasets: [{
            label: "Films Count",
            data: counts,
            backgroundColor: [
              "#008fd5",
              "#facc15",
              "#f59e0b",
              "#f97316",
              "#ef4444",
              "#ff2700",
            ],
            borderRadius: 6,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, grid: { color: currentTheme === "dark" ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.06)" } },
            x: { grid: { display: false } }
          }
        }
      });
    }

    const tbody = document.querySelector("#discrepancyMatrixTable tbody");
    if (tbody) {
      tbody.innerHTML = data.breakdown.map(row => `
        <tr>
          <td><strong>+${Number(row.difference).toFixed(1)} Stars</strong></td>
          <td>${row.count} films</td>
          <td>
            <div style="display: flex; align-items: center; gap: 0.6rem;">
              <div style="background: ${row.difference >= 0.4 ? 'var(--fte-crimson)' : 'var(--fte-gold)'}; height: 6px; width: ${row.percentage * 2}px; border-radius: 3px;"></div>
              <span>${row.percentage}%</span>
            </div>
          </td>
        </tr>
      `).join("");
    }
  } catch (err) {
    console.error("Discrepancies error:", err);
  }
}

// 8. Platforms & KDE Curves
async function loadPlatforms() {
  try {
    const data = await safeFetchJson(`${API_BASE}/api/platforms`, 'platforms');
    if (!data) return;

    const tbody = document.querySelector("#platformBenchmarkTable tbody");
    if (tbody) {
      tbody.innerHTML = data.summary_table.map(row => `
        <tr>
          <td><strong>${row.platform}</strong></td>
          <td><strong style="color: ${row.platform.includes('Fandango (Displayed)') ? 'var(--fte-crimson)' : 'var(--text-main)'};">${Number(row.mean).toFixed(2)} ★</strong></td>
          <td>${Number(row.median).toFixed(2)}</td>
          <td>${Number(row.std).toFixed(2)}</td>
          <td>${Number(row.min).toFixed(2)} - ${Number(row.max).toFixed(2)}</td>
          <td>${Number(row.q25).toFixed(2)} - ${Number(row.q75).toFixed(2)}</td>
        </tr>
      `).join("");
    }

    const ctx = document.getElementById("platformKdeChart")?.getContext("2d");
    if (ctx && typeof Chart !== "undefined" && data.kde_curves) {
      if (chartInstances.platformKde) chartInstances.platformKde.destroy();

      const kde = data.kde_curves;
      chartInstances.platformKde = new Chart(ctx, {
        type: "line",
        data: {
          labels: kde.x,
          datasets: [
            {
              label: "Fandango (Displayed Stars)",
              data: kde["Fandango (Displayed)"],
              borderColor: "#ff2700",
              backgroundColor: "rgba(255, 39, 0, 0.12)",
              borderWidth: 3,
              fill: true,
              tension: 0.35,
              pointRadius: 0,
            },
            {
              label: "Fandango (Actual HTML)",
              data: kde["Fandango (Actual HTML)"],
              borderColor: "#008fd5",
              borderDash: [4, 4],
              borderWidth: 2,
              fill: false,
              tension: 0.35,
              pointRadius: 0,
            },
            {
              label: "Rotten Tomatoes (Norm)",
              data: kde["Rotten Tomatoes (Norm)"],
              borderColor: "#fa320a",
              borderWidth: 2,
              fill: false,
              tension: 0.35,
              pointRadius: 0,
            },
            {
              label: "Metacritic (Norm)",
              data: kde["Metacritic (Norm)"],
              borderColor: "#339900",
              borderWidth: 2,
              fill: false,
              tension: 0.35,
              pointRadius: 0,
            },
            {
              label: "IMDB (Norm)",
              data: kde["IMDB (Norm)"],
              borderColor: "#e5a900",
              borderWidth: 2,
              fill: false,
              tension: 0.35,
              pointRadius: 0,
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: {
                color: currentTheme === "dark" ? "#cbd5e1" : "#334155",
                font: { family: "'Plus Jakarta Sans', sans-serif", size: 11, weight: "600" }
              }
            }
          },
          scales: {
            x: {
              title: { display: true, text: "Standardized 5-Star Rating Scale", color: currentTheme === "dark" ? "#94a3b8" : "#475569" },
              grid: { color: currentTheme === "dark" ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.06)" }
            },
            y: {
              title: { display: true, text: "Density", color: currentTheme === "dark" ? "#94a3b8" : "#475569" },
              grid: { color: currentTheme === "dark" ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.06)" }
            }
          }
        }
      });
    }
  } catch (err) {
    console.error("Platforms error:", err);
  }
}

// 9. Temporal Shift
async function loadTemporal() {
  try {
    const data = await safeFetchJson(`${API_BASE}/api/temporal`, 'temporal');
    if (!data) return;

    const ctx = document.getElementById("temporalKdeChart")?.getContext("2d");
    if (ctx && typeof Chart !== "undefined" && data.kde_curves) {
      if (chartInstances.temporalKde) chartInstances.temporalKde.destroy();

      const kde = data.kde_curves;
      chartInstances.temporalKde = new Chart(ctx, {
        type: "line",
        data: {
          labels: kde.x,
          datasets: [
            {
              label: "2015 Pre-Article Displayed (Mean: 4.09 ★)",
              data: kde.kde_2015_displayed,
              borderColor: "#ff2700",
              backgroundColor: "rgba(255, 39, 0, 0.12)",
              borderWidth: 2.5,
              fill: true,
              tension: 0.35,
              pointRadius: 0,
            },
            {
              label: "2015 Pre-Article True HTML (Mean: 3.85 ★)",
              data: kde.kde_2015_actual,
              borderColor: "#008fd5",
              borderDash: [4, 4],
              borderWidth: 2,
              fill: false,
              tension: 0.35,
              pointRadius: 0,
            },
            {
              label: "2016-17 Post-Article Displayed (Mean: 3.89 ★)",
              data: kde.kde_2016_17_displayed,
              borderColor: "#10b981",
              backgroundColor: "rgba(16, 185, 129, 0.12)",
              borderWidth: 2.5,
              fill: true,
              tension: 0.35,
              pointRadius: 0,
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: {
                color: currentTheme === "dark" ? "#cbd5e1" : "#334155",
                font: { family: "'Plus Jakarta Sans', sans-serif", size: 11, weight: "600" }
              }
            }
          },
          scales: {
            x: {
              title: { display: true, text: "Fandango Star Rating Scale (0 to 5)", color: currentTheme === "dark" ? "#94a3b8" : "#475569" },
              grid: { color: currentTheme === "dark" ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.06)" }
            },
            y: {
              title: { display: true, text: "Density", color: currentTheme === "dark" ? "#94a3b8" : "#475569" },
              grid: { color: currentTheme === "dark" ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.06)" }
            }
          }
        }
      });
    }
  } catch (err) {
    console.error("Temporal error:", err);
  }
}

// 10. Scale Normalization Converter Playground
function initScaleConverter() {
  const rtInput = document.getElementById("convRTInput");
  const metaInput = document.getElementById("convMetaInput");
  const imdbInput = document.getElementById("convIMDBInput");

  function updateConverter() {
    const rt = parseFloat(rtInput?.value || 0);
    const meta = parseFloat(metaInput?.value || 0);
    const imdb = parseFloat(imdbInput?.value || 0);

    const rtNorm = (rt / 20.0).toFixed(2);
    const metaNorm = (meta / 20.0).toFixed(2);
    const imdbNorm = (imdb / 2.0).toFixed(2);

    document.getElementById("convRTNorm").textContent = `${rtNorm} ★`;
    document.getElementById("convMetaNorm").textContent = `${metaNorm} ★`;
    document.getElementById("convIMDBNorm").textContent = `${imdbNorm} ★`;

    const avgNorm = ((parseFloat(rtNorm) + parseFloat(metaNorm) + parseFloat(imdbNorm)) / 3.0).toFixed(2);
    document.getElementById("convAvgNorm").textContent = `${avgNorm} ★`;
  }

  rtInput?.addEventListener("input", updateConverter);
  metaInput?.addEventListener("input", updateConverter);
  imdbInput?.addEventListener("input", updateConverter);
  updateConverter();
}

// 11. Ticket Sales Conflict Simulator
function initTicketImpactSimulator() {
  const priceSlider = document.getElementById("ticketPriceSlider");
  const visitorsSlider = document.getElementById("visitorsSlider");

  function updateRevenue() {
    const price = parseFloat(priceSlider?.value || 12);
    const visitors = parseInt(visitorsSlider?.value || 500000);

    document.getElementById("priceValDisplay").textContent = `$${price.toFixed(2)}`;
    document.getElementById("visitorsValDisplay").textContent = visitors.toLocaleString();

    // Baseline conversion @ 3.5 stars = 4.2%
    // Glitched conversion @ 4.5 stars = 5.8% (+1.6% absolute conversion boost)
    const baseTickets = visitors * 0.042;
    const boostedTickets = visitors * 0.058;
    const extraTickets = boostedTickets - baseTickets;
    const extraRevenue = extraTickets * price;

    document.getElementById("simExtraTickets").textContent = Math.round(extraTickets).toLocaleString();
    document.getElementById("simExtraRevenue").textContent = `$${Math.round(extraRevenue).toLocaleString()}`;
  }

  priceSlider?.addEventListener("input", updateRevenue);
  visitorsSlider?.addEventListener("input", updateRevenue);
  updateRevenue();
}

// 12. Statistical Lab
async function loadStats() {
  try {
    const data = await safeFetchJson(`${API_BASE}/api/stats`, 'stats');
    if (!data) return;

    const inf = data.inflation_test;
    const temp = data.temporal_test;

    const container = document.getElementById("statsLabContent");
    if (container) {
      container.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.75rem;">
          <div class="plot-card">
            <h3 style="font-family: var(--font-serif); font-size: 1.3rem; margin-bottom: 0.5rem;">1. Paired Inflation Test (2015 Dataset)</h3>
            <p style="color: var(--text-dim); font-size: 0.82rem; margin-bottom: 1rem;">Testing H₀: μ_diff = 0 vs H₁: μ_diff &gt; 0 (Right-Tailed Paired Test)</p>
            <table class="data-table">
              <tr><td>Sample Size (N)</td><td><strong>${inf.sample_size} theatrical releases</strong></td></tr>
              <tr><td>Mean Inflation Discrepancy</td><td><strong style="color: var(--fte-crimson);">+${Number(inf.mean_difference).toFixed(3)} stars</strong></td></tr>
              <tr><td>Standard Error (SE)</td><td>${Number(inf.standard_error).toFixed(4)}</td></tr>
              <tr><td>Paired t-Statistic</td><td><strong>t = ${Number(inf.t_statistic).toFixed(2)}</strong></td></tr>
              <tr><td>p-Value</td><td><strong style="color: var(--fte-crimson);">&lt; 10⁻¹⁵ (Extremely Significant)</strong></td></tr>
              <tr><td>Cohen's d Effect Size</td><td><strong style="color: var(--fte-gold);">${Number(inf.cohens_d).toFixed(2)} (${inf.effect_interpretation})</strong></td></tr>
              <tr><td>95% Bootstrap Confidence Interval</td><td><strong>[+${Number(inf.bootstrap_95_ci[0]).toFixed(3)}, +${Number(inf.bootstrap_95_ci[1]).toFixed(3)}] stars</strong></td></tr>
            </table>
          </div>

          <div class="plot-card">
            <h3 style="font-family: var(--font-serif); font-size: 1.3rem; margin-bottom: 0.5rem;">2. Post-Article Shift (2015 vs 2016–17)</h3>
            <p style="color: var(--text-dim); font-size: 0.82rem; margin-bottom: 1rem;">Testing H₀: μ_2015 = μ_2016-17 vs H₁: μ_2015 ≠ μ_2016-17</p>
            <table class="data-table">
              <tr><td>Sample Sizes</td><td>2015: <strong>${temp.sample_size_2015}</strong> | 2016-17: <strong>${temp.sample_size_2016_17}</strong></td></tr>
              <tr><td>2015 Displayed Mean</td><td><strong>${Number(temp.mean_2015).toFixed(2)} stars</strong></td></tr>
              <tr><td>2016-17 Displayed Mean</td><td><strong>${Number(temp.mean_2016_17).toFixed(2)} stars</strong></td></tr>
              <tr><td>Net Drop in Displayed Ratings</td><td><strong style="color: var(--fte-green);">${Number(temp.mean_difference).toFixed(2)} stars</strong></td></tr>
              <tr><td>Welch's t-Statistic</td><td><strong>t = ${Number(temp.t_statistic).toFixed(2)} (p = 0.0008)</strong></td></tr>
              <tr><td>Kolmogorov-Smirnov Test</td><td><strong>D = ${Number(temp.ks_statistic).toFixed(3)} (p = 0.0003)</strong></td></tr>
              <tr><td>Cohen's d</td><td><strong>${Number(temp.cohens_d).toFixed(2)}</strong></td></tr>
            </table>
          </div>
        </div>
      `;
    }
  } catch (err) {
    console.error("Stats error:", err);
  }
}

// 13. Film Explorer & Filters
function initFilmExplorerEvents() {
  const searchInput = document.getElementById("filmSearchInput");
  const chips = document.querySelectorAll(".chip-btn");

  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      chips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      activeFilter = chip.getAttribute("data-filter");
      renderFilteredFilms();
    });
  });

  searchInput?.addEventListener("input", debounce(() => renderFilteredFilms(), 200));
}

function renderFilteredFilms() {
  const searchInput = document.getElementById("filmSearchInput");
  const query = searchInput?.value.toLowerCase().trim() || "";
  let filtered = [...allMoviesData];

  if (query) {
    filtered = filtered.filter(m => m.film.toLowerCase().includes(query));
  }

  if (activeFilter === "max-inflation") {
    filtered = filtered.filter(m => m.discrepancy >= 0.5);
  } else if (activeFilter === "high-votes") {
    filtered = filtered.filter(m => m.votes >= 10000);
  } else if (activeFilter === "rt-gap") {
    filtered = filtered.filter(m => (m.fandango_stars - m.rt_norm) >= 1.5);
  } else if (activeFilter === "five-stars") {
    filtered = filtered.filter(m => m.fandango_stars === 5.0);
  }

  const tbody = document.querySelector("#filmExplorerTable tbody");
  const countEl = document.getElementById("filmCountLabel");
  if (countEl) countEl.textContent = `${filtered.length} of ${allMoviesData.length} films`;

  if (tbody) {
    if (filtered.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-dim); padding: 2rem;">No matching films found.</td></tr>`;
      return;
    }

    tbody.innerHTML = filtered.map(m => `
      <tr onclick="updateSpotlightByName('${m.film.replace(/'/g, "\\'")}')">
        <td><strong>${m.film}</strong></td>
        <td><span style="color: var(--fte-gold); font-size: 1rem;">${getVisualStars(m.fandango_stars)}</span> <strong>${Number(m.fandango_stars).toFixed(1)}</strong></td>
        <td>${Number(m.fandango_actual).toFixed(2)}</td>
        <td><span class="diff-badge">+${Number(m.discrepancy).toFixed(2)}</span></td>
        <td>${Number(m.rt_norm).toFixed(2)}</td>
        <td>${Number(m.metacritic_norm).toFixed(2)}</td>
        <td>${Number(m.imdb_norm).toFixed(2)}</td>
        <td>${Number(m.votes).toLocaleString()}</td>
      </tr>
    `).join("");
  }
}

// 14. SQL Workbench
async function loadSQLPresets() {
  const sidebar = document.getElementById("sqlQueryPills");
  const sqlEditor = document.getElementById("sqlWorkbenchEditor");

  try {
    const presets = await safeFetchJson(`${API_BASE}/api/presets`, 'presets');
    if (!presets) return;

    if (sidebar) {
      sidebar.innerHTML = presets.map(p => `
        <button class="preset-btn" data-qid="${p.id}">
          ${p.title}
        </button>
      `).join("");

      sidebar.querySelectorAll(".preset-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const qid = btn.getAttribute("data-qid");
          const found = presets.find(q => q.id === qid);
          if (found && sqlEditor) {
            sqlEditor.value = found.query;
            runWorkbenchSQL();
          }
        });
      });
    }
  } catch (err) {
    console.error("SQL Presets error:", err);
  }
}

function initSQLWorkbenchEvents() {
  const runBtn = document.getElementById("btnRunWorkbenchSQL");
  runBtn?.addEventListener("click", runWorkbenchSQL);
}

async function runWorkbenchSQL() {
  const sqlEditor = document.getElementById("sqlWorkbenchEditor");
  const query = sqlEditor?.value.trim();
  if (!query) return;

  const resultBox = document.getElementById("sqlWorkbenchResults");
  if (resultBox) {
    resultBox.innerHTML = `<div style="padding: 1rem; color: var(--text-dim);">Executing query...</div>`;
  }

  const t0 = performance.now();
  try {
    const res = await fetch(`${API_BASE}/api/sql`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query, limit: 100 })
    });
    const data = await res.json();
    const elapsed = (performance.now() - t0).toFixed(1);

    if (!data.success) {
      resultBox.innerHTML = `
        <div style="background: var(--fte-crimson-subtle); border-left: 3px solid var(--fte-crimson); padding: 1rem; border-radius: 6px; margin-top: 1rem; font-size: 0.85rem;">
          <strong>SQL Error:</strong> ${data.error}
        </div>
      `;
      return;
    }

    const headers = data.columns.map(c => `<th>${c}</th>`).join("");
    const rows = data.rows.map(r => {
      const cells = data.columns.map(c => `<td>${r[c] !== null ? r[c] : '<em>NULL</em>'}</td>`).join("");
      return `<tr>${cells}</tr>`;
    }).join("");

    resultBox.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin: 1rem 0 0.5rem 0; font-size: 0.78rem; color: var(--text-dim);">
        <span>${data.row_count} rows returned</span>
        <span>Execution time: ${elapsed} ms</span>
      </div>
      <div class="data-table-container">
        <table class="data-table">
          <thead><tr>${headers}</tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    `;
  } catch (err) {
    if (resultBox) resultBox.innerHTML = `<div style="color: var(--fte-crimson);">Error: ${err.message}</div>`;
  }
}

// 15. CSV Export Button
function initExportButton() {
  const exportBtn = document.getElementById("btnExportDataset");
  exportBtn?.addEventListener("click", () => {
    if (!allMoviesData || allMoviesData.length === 0) return;
    const headers = ["FILM", "Fandango_Stars", "Fandango_Actual", "Discrepancy", "RT_norm", "Metacritic_norm", "IMDB_norm", "Votes"];
    const rows = allMoviesData.map(m => [
      `"${m.film.replace(/"/g, '""')}"`,
      m.fandango_stars,
      m.fandango_actual,
      m.discrepancy,
      m.rt_norm,
      m.metacritic_norm,
      m.imdb_norm,
      m.votes
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "fandango_audited_2015_dataset.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });
}

function debounce(fn, wait) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), wait);
  };
}
