/**
 * v_rate_movies • Bento Grid Intelligence Experience
 * Author: vartiwa (varunt154@gmail.com)
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
  const tabs = document.querySelectorAll(".pill-tab, .nav-tab");
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

// 3. Glitch Simulator (Hero Feature)
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
        glitchDeltaEl.innerHTML = `<span style="color: var(--accent-crimson); font-weight: 700;">+${delta} ★ Inflation Penalty</span>`;
      } else {
        glitchDeltaEl.innerHTML = `<span style="color: var(--accent-emerald); font-weight: 700;">0.0 ★ Normal Unbiased</span>`;
      }
    }

    if (simNoteEl) {
      if (frac >= 0.1 && frac < 0.25) {
        simNoteEl.textContent = `Glitch Active: A score of ${trueScore.toFixed(1)} is mathematically 4.0★, but Fandango pushed it up to 4.5★!`;
      } else if (frac >= 0.6 && frac < 0.75) {
        simNoteEl.textContent = `Glitch Active: A score of ${trueScore.toFixed(1)} is mathematically 4.5★, but Fandango pushed it up to 5.0★!`;
      } else {
        simNoteEl.textContent = `Standard rounding point.`;
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
    // fallback
  }
  if (typeof EMBEDDED_DATA !== "undefined" && EMBEDDED_DATA[embeddedKey]) {
    return EMBEDDED_DATA[embeddedKey];
  }
  return null;
}

// 5. Overview KPIs
async function loadOverview() {
  try {
    const data = await safeFetchJson(`${API_BASE}/api/overview`, 'overview');
    if (!data) return;

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
    <div class="movie-mini-card">
      <div class="movie-mini-title" title="${d.film}">${d.film}</div>
      <div class="movie-mini-stars">${getVisualStars(d.fandango_stars)}</div>
      <div style="display: flex; justify-content: space-between; align-items: center; background: var(--bg-card-subtle); padding: 0.5rem 0.75rem; border-radius: var(--radius-sm); margin-bottom: 0.6rem; font-size: 0.8rem;">
        <span>RT Critics: <strong style="color: var(--color-rt);">${d.rt_raw}%</strong></span>
        <span>Fandango: <strong style="color: var(--accent-primary);">${d.fandango_stars.toFixed(1)}★</strong></span>
      </div>
      <div class="movie-mini-footer">
        <span>True HTML: ${d.fandango_actual.toFixed(2)}</span>
        <span class="widget-badge danger">+${d.gap.toFixed(2)} ★ Gap</span>
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
          borderColor: "rgba(148, 163, 184, 0.4)",
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
            if (diff >= 0.5) return "#f43f5e";
            if (diff >= 0.4) return "#f59e0b";
            if (diff >= 0.2) return "#fbbf24";
            return "#6366f1";
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
          backgroundColor: currentTheme === "dark" ? "#1e293b" : "#0f172a",
          titleColor: "#ffffff",
          titleFont: { family: "'Plus Jakarta Sans', sans-serif", weight: "700", size: 13 },
          bodyColor: "#cbd5e1",
          bodyFont: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
          padding: 12,
          borderRadius: 8,
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
          title: { display: true, text: "True Underlying HTML Rating (Unrounded)", color: "#94a3b8", font: { weight: "700", size: 11 } },
          grid: { color: currentTheme === "dark" ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.04)" }
        },
        y: {
          min: 2.5,
          max: 5.2,
          title: { display: true, text: "Displayed Stars on Fandango", color: "#94a3b8", font: { weight: "700", size: 11 } },
          grid: { color: currentTheme === "dark" ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.04)" }
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
    <div class="movie-mini-card" onclick="updateSpotlightByName('${m.film.replace(/'/g, "\\'")}')">
      <div class="movie-mini-title" title="${m.film}">${m.film}</div>
      <div class="movie-mini-stars">${getVisualStars(m.fandango_stars)}</div>
      <div class="movie-mini-footer">
        <span>True: <strong>${Number(m.fandango_actual).toFixed(2)} / 5.0</strong></span>
        <span class="widget-badge danger">+${Number(m.discrepancy).toFixed(2)} ★</span>
      </div>
    </div>
  `).join("");
}

window.updateSpotlightByName = (name) => {
  const found = allMoviesData.find(m => m.film === name);
  if (found) {
    updateSpotlight(found);
    window.scrollTo({ top: document.getElementById('parityScatterChart')?.offsetTop - 120 || 0, behavior: 'smooth' });
  }
};

function getVisualStars(rating) {
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.4 ? 1 : 0;
  const empty = 5 - full - half;
  return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(empty);
}

// 7. Discrepancy Breakdown (Bento Pill Bars)
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
              "#6366f1",
              "#818cf8",
              "#a5b4fc",
              "#fbbf24",
              "#f59e0b",
              "#f43f5e",
            ],
            borderRadius: 8,
            borderSkipped: false,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, grid: { color: currentTheme === "dark" ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.04)" } },
            x: { grid: { display: false } }
          }
        }
      });
    }
  } catch (err) {
    console.error("Discrepancies error:", err);
  }
}

// 8. Platforms Benchmark (Spline Density)
async function loadPlatforms() {
  try {
    const data = await safeFetchJson(`${API_BASE}/api/platforms`, 'platforms');
    if (!data) return;

    const tbody = document.querySelector("#platformBenchmarkTable tbody");
    if (tbody) {
      tbody.innerHTML = data.summary_table.map(row => `
        <tr>
          <td><strong>${row.platform}</strong></td>
          <td><strong style="color: ${row.platform.includes('Fandango (Displayed)') ? 'var(--accent-crimson)' : 'var(--text-main)'};">${Number(row.mean).toFixed(2)} ★</strong></td>
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
              label: "Fandango (Displayed)",
              data: kde["Fandango (Displayed)"],
              borderColor: "#6366f1",
              backgroundColor: "rgba(99, 102, 241, 0.15)",
              borderWidth: 2.5,
              fill: true,
              tension: 0.4,
              pointRadius: 0,
            },
            {
              label: "Rotten Tomatoes",
              data: kde["Rotten Tomatoes (Norm)"],
              borderColor: "#f43f5e",
              borderWidth: 2,
              fill: false,
              tension: 0.4,
              pointRadius: 0,
            },
            {
              label: "Metacritic",
              data: kde["Metacritic (Norm)"],
              borderColor: "#10b981",
              borderWidth: 2,
              fill: false,
              tension: 0.4,
              pointRadius: 0,
            },
            {
              label: "IMDB",
              data: kde["IMDB (Norm)"],
              borderColor: "#f59e0b",
              borderWidth: 2,
              fill: false,
              tension: 0.4,
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
              title: { display: true, text: "Standardized 5-Star Rating Scale", color: "#94a3b8" },
              grid: { color: currentTheme === "dark" ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.04)" }
            },
            y: {
              title: { display: true, text: "Density", color: "#94a3b8" },
              grid: { color: currentTheme === "dark" ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.04)" }
            }
          }
        }
      });
    }
  } catch (err) {
    console.error("Platforms error:", err);
  }
}

// 9. Temporal Shift (Spline Comparison)
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
              label: "2015 Pre-Article Displayed (4.09★)",
              data: kde.kde_2015_displayed,
              borderColor: "#f43f5e",
              backgroundColor: "rgba(244, 63, 94, 0.12)",
              borderWidth: 2.5,
              fill: true,
              tension: 0.4,
              pointRadius: 0,
            },
            {
              label: "2016-17 Post-Article Displayed (3.89★)",
              data: kde.kde_2016_17_displayed,
              borderColor: "#10b981",
              backgroundColor: "rgba(16, 185, 129, 0.15)",
              borderWidth: 2.5,
              fill: true,
              tension: 0.4,
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
              title: { display: true, text: "Fandango Star Rating Scale (0 to 5)", color: "#94a3b8" },
              grid: { color: currentTheme === "dark" ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.04)" }
            },
            y: {
              title: { display: true, text: "Density", color: "#94a3b8" },
              grid: { color: currentTheme === "dark" ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.04)" }
            }
          }
        }
      });
    }
  } catch (err) {
    console.error("Temporal error:", err);
  }
}

// 10. Statistical Lab
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
          <div class="nested-widget">
            <h3 style="font-family: var(--font-serif); font-size: 1.3rem; margin-bottom: 0.5rem;">1. Paired Inflation Test (2015 Dataset)</h3>
            <p style="color: var(--text-dim); font-size: 0.82rem; margin-bottom: 1rem;">Testing H₀: μ_diff = 0 vs H₁: μ_diff &gt; 0 (Right-Tailed Paired Test)</p>
            <table class="bento-table">
              <tr><td>Sample Size (N)</td><td><strong>${inf.sample_size} theatrical releases</strong></td></tr>
              <tr><td>Mean Inflation Discrepancy</td><td><strong style="color: var(--accent-crimson);">+${Number(inf.mean_difference).toFixed(3)} stars</strong></td></tr>
              <tr><td>Standard Error (SE)</td><td>${Number(inf.standard_error).toFixed(4)}</td></tr>
              <tr><td>Paired t-Statistic</td><td><strong>t = ${Number(inf.t_statistic).toFixed(2)}</strong></td></tr>
              <tr><td>p-Value</td><td><strong style="color: var(--accent-crimson);">&lt; 10⁻¹⁵ (Extremely Significant)</strong></td></tr>
              <tr><td>Cohen's d Effect Size</td><td><strong style="color: var(--accent-amber);">${Number(inf.cohens_d).toFixed(2)} (${inf.effect_interpretation})</strong></td></tr>
              <tr><td>95% Bootstrap Confidence Interval</td><td><strong>[+${Number(inf.bootstrap_95_ci[0]).toFixed(3)}, +${Number(inf.bootstrap_95_ci[1]).toFixed(3)}] stars</strong></td></tr>
            </table>
          </div>

          <div class="nested-widget">
            <h3 style="font-family: var(--font-serif); font-size: 1.3rem; margin-bottom: 0.5rem;">2. Post-Article Shift (2015 vs 2016–17)</h3>
            <p style="color: var(--text-dim); font-size: 0.82rem; margin-bottom: 1rem;">Testing H₀: μ_2015 = μ_2016-17 vs H₁: μ_2015 ≠ μ_2016-17</p>
            <table class="bento-table">
              <tr><td>Sample Sizes</td><td>2015: <strong>${temp.sample_size_2015}</strong> | 2016-17: <strong>${temp.sample_size_2016_17}</strong></td></tr>
              <tr><td>2015 Displayed Mean</td><td><strong>${Number(temp.mean_2015).toFixed(2)} stars</strong></td></tr>
              <tr><td>2016-17 Displayed Mean</td><td><strong>${Number(temp.mean_2016_17).toFixed(2)} stars</strong></td></tr>
              <tr><td>Net Drop in Displayed Ratings</td><td><strong style="color: var(--accent-emerald);">${Number(temp.mean_difference).toFixed(2)} stars</strong></td></tr>
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

// 11. Film Explorer & Filters
function initFilmExplorerEvents() {
  const searchInput = document.getElementById("filmSearchInput");
  const chips = document.querySelectorAll(".filter-chip");

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
        <td><span style="color: var(--accent-amber); font-size: 1rem;">${getVisualStars(m.fandango_stars)}</span> <strong>${Number(m.fandango_stars).toFixed(1)}</strong></td>
        <td>${Number(m.fandango_actual).toFixed(2)}</td>
        <td><span class="widget-badge danger">+${Number(m.discrepancy).toFixed(2)}</span></td>
        <td>${Number(m.rt_norm).toFixed(2)}</td>
        <td>${Number(m.metacritic_norm).toFixed(2)}</td>
        <td>${Number(m.imdb_norm).toFixed(2)}</td>
        <td>${Number(m.votes).toLocaleString()}</td>
      </tr>
    `).join("");
  }
}

// 12. SQL Console Presets
async function loadSQLPresets() {
  const sidebar = document.getElementById("sqlQueryPills");
  const sqlEditor = document.getElementById("sqlWorkbenchEditor");

  try {
    const presets = await safeFetchJson(`${API_BASE}/api/presets`, 'presets');
    if (!presets) return;

    if (sidebar) {
      sidebar.innerHTML = presets.map(p => `
        <button class="preset-pill-btn" data-qid="${p.id}">
          ${p.title}
        </button>
      `).join("");

      sidebar.querySelectorAll(".preset-pill-btn").forEach(btn => {
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
        <div style="background: rgba(244,63,94,0.1); border-left: 3px solid var(--accent-crimson); padding: 1rem; border-radius: 8px; margin-top: 1rem; font-size: 0.85rem;">
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
        <table class="bento-table">
          <thead><tr>${headers}</tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    `;
  } catch (err) {
    if (resultBox) resultBox.innerHTML = `<div style="color: var(--accent-crimson);">Error: ${err.message}</div>`;
  }
}

// 13. CSV Export
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
    link.setAttribute("download", "v_rate_movies_clean_dataset.csv");
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
