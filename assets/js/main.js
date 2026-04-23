const TOUR_STATE_KEY = "pad-tour-state";
const TOUR_DATA_URL = "/assets/data/tour_students.json";
const TOUR_PARAMS_URL = "/assets/data/tour_students_settings.json";

function hasStoredValue(key) {
    const value = sessionStorage.getItem(key);
    return value && value !== "null" && value !== "undefined";
}

function setSessionJson(key, value) {
    sessionStorage.setItem(key, JSON.stringify(value));
}

function getSessionJson(key) {
    const raw = sessionStorage.getItem(key);
    if (!raw) {
        return null;
    }

    try {
        return JSON.parse(raw);
    } catch (error) {
        return null;
    }
}

function getTourState() {
    return getSessionJson(TOUR_STATE_KEY);
}

function setTourState(state) {
    setSessionJson(TOUR_STATE_KEY, state);
}

function clearTourState() {
    sessionStorage.removeItem(TOUR_STATE_KEY);
}

async function loadTourAssets() {
    const [dataResponse, paramsResponse] = await Promise.all([
        fetch(TOUR_DATA_URL),
        fetch(TOUR_PARAMS_URL),
    ]);

    if (!dataResponse.ok || !paramsResponse.ok) {
        throw new Error("Could not load the sample dataset for the guided tour.");
    }

    return {
        data: await dataResponse.json(),
        params: await paramsResponse.json(),
    };
}

async function tour() {
    try {
        const sample = await loadTourAssets();
        setSessionJson("data-store", sample.data);
        setSessionJson("data-filename-store", "tour_students.csv");
        setSessionJson("params-store", sample.params);
        setSessionJson("params-filename-store", "tour_students_settings.json");
        setSessionJson(
            "aggregation-method-store",
            sample.params._aggregation_method || "R"
        );
        setTourState({ page: "upload" });
        window.location.href = "/upload";
    } catch (error) {
        clearTourState();
        window.alert(error.message);
    }
}

window.tour = tour;

function updateStepperLinks() {
    const hasData = hasStoredValue("data-store");
    const hasParams = hasStoredValue("params-store");
    const steps = document.querySelectorAll(".bs-stepper-header .step");

    if (steps.length >= 4) {
        const step3 = steps[2];
        if (step3) {
            const step3Link = step3.querySelector(".step-trigger");
            if (step3Link) {
                if (!hasData) {
                    step3Link.onclick = function (e) { e.preventDefault(); return false; };
                    step3Link.style.cursor = "not-allowed";
                    step3Link.style.opacity = "0.5";
                    step3Link.style.pointerEvents = "none";
                } else {
                    step3Link.onclick = null;
                    step3Link.style.cursor = "pointer";
                    step3Link.style.opacity = "1";
                    step3Link.style.pointerEvents = "auto";
                }
            }
        }

        const step4 = steps[3];
        if (step4) {
            const step4Link = step4.querySelector(".step-trigger");
            if (step4Link) {
                if (!hasParams || !hasData) {
                    step4Link.onclick = function (e) { e.preventDefault(); return false; };
                    step4Link.style.cursor = "not-allowed";
                    step4Link.style.opacity = "0.5";
                    step4Link.style.pointerEvents = "none";
                } else {
                    step4Link.onclick = null;
                    step4Link.style.cursor = "pointer";
                    step4Link.style.opacity = "1";
                    step4Link.style.pointerEvents = "auto";
                }
            }
        }
    }
}

function startIntroWhenReady(selectors, builder, attempt = 0) {
    const maxAttempts = 40;
    const allPresent = selectors.every((selector) => document.querySelector(selector));
    if (allPresent) {
        builder();
        return;
    }

    if (attempt >= maxAttempts) {
        clearTourState();
        return;
    }

    window.setTimeout(
        () => startIntroWhenReady(selectors, builder, attempt + 1),
        250
    );
}

function runPageTour() {
    const tourState = getTourState();
    if (!tourState || typeof introJs === "undefined") {
        return;
    }

    const path = window.location.pathname.replace(/\/+$/, "") || "/";
    const intro = introJs();

    if (tourState.page === "upload" && path === "/upload") {
        startIntroWhenReady(
            ["#upload-csv-data-preview", "#upload-params-data-preview", "#upload-submit-btn"],
            () => {
                intro.setOptions({
                    showProgress: true,
                    exitOnOverlayClick: false,
                    doneLabel: "Continue",
                    steps: [
                        {
                            element: "#upload-csv-data-preview",
                            intro: "The tour starts with a sample dataset already loaded into this session, so you can focus on the workflow instead of file preparation.",
                        },
                        {
                            element: "#upload-params-data-preview",
                            intro: "The criteria template is prefilled too. In the next step you can review weights, ranges, and the ranking method.",
                        },
                        {
                            element: "#upload-submit-btn",
                            intro: "Move to Step 3 to choose the aggregation method and confirm the criteria setup.",
                        },
                    ],
                });
                intro.oncomplete(() => {
                    setTourState({ page: "criteria" });
                    document.getElementById("upload-submit-btn").click();
                });
                intro.onexit(clearTourState);
                intro.start();
            }
        );
        return;
    }

    if (tourState.page === "criteria" && path === "/criteria") {
        startIntroWhenReady(
            ["#criteria-method-section", "#criteria-edit-card", "#criteria-submit-btn"],
            () => {
                intro.setOptions({
                    showProgress: true,
                    exitOnOverlayClick: false,
                    doneLabel: "Analyze",
                    steps: [
                        {
                            element: "#criteria-method-section",
                            intro: "Step 3 now includes the ranking method choice, so the wizard keeps the main decision in the main flow instead of hiding it in settings.",
                        },
                        {
                            element: "#criteria-edit-card",
                            intro: "Review the ID column, weights, expert ranges, and objectives here. The sample settings are editable if you want to explore a different setup.",
                        },
                        {
                            element: "#criteria-submit-btn",
                            intro: "Continue to the analysis dashboard once the configuration looks right.",
                        },
                    ],
                });
                intro.oncomplete(() => {
                    setTourState({ page: "dashboard" });
                    document.getElementById("criteria-submit-btn").click();
                });
                intro.onexit(clearTourState);
                intro.start();
            }
        );
        return;
    }

    if (tourState.page === "dashboard" && path === "/dashboard") {
        startIntroWhenReady(
            ["#ranking-fig", "#ranking-datatable"],
            () => {
                intro.setOptions({
                    showProgress: true,
                    exitOnOverlayClick: false,
                    doneLabel: "Finish",
                    steps: [
                        {
                            element: "#ranking-fig",
                            intro: "The analysis view now reflects the ranking method selected in Step 3. Score-based methods use a clean bar chart with the alternative IDs shown on the x-axis.",
                        },
                        {
                            element: "#ranking-datatable",
                            intro: "Use the ranking table to inspect the ordered alternatives and select rows for deeper postfactum analysis.",
                        },
                    ],
                });
                intro.oncomplete(clearTourState);
                intro.onexit(clearTourState);
                intro.start();
            }
        );
    }
}

document.addEventListener("DOMContentLoaded", function () {
    updateStepperLinks();
    runPageTour();
    setInterval(updateStepperLinks, 500);
});

updateStepperLinks();
