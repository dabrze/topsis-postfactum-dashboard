////////////////
// Footer
////////////////
// function updateFooter() {
//     var footerH = $("#footer").height();
//     var contentH = $("#header").height() + $("#page-content").height();
//     var windowH = $(window).height();

//     if (contentH + footerH > windowH) {
//         $("#footer").removeClass("fixed");
//     } else {
//         $("#footer").addClass("fixed");
//     }
// }


// $(document).ready(function () {
//     $(window).resize(function () {
//         updateFooter();
//     });

//     updateFooter();
//     setTimeout(function () { updateFooter(); }, 150)
//     setTimeout(function () { updateFooter(); }, 500)
//     setTimeout(function () { updateFooter(); }, 1000)
//     //startTutorial()
// });
////////////////
// Stepper Navigation Control
////////////////
function updateStepperLinks() {
    // Get session storage data
    const dataStore = sessionStorage.getItem('data-store');
    const paramsStore = sessionStorage.getItem('params-store');

    // Check if data/params exist (not null and not undefined)
    const hasData = dataStore && dataStore !== 'null' && dataStore !== 'undefined';
    const hasParams = paramsStore && paramsStore !== 'null' && paramsStore !== 'undefined';

    // Get all step links
    const steps = document.querySelectorAll('.bs-stepper-header .step');

    if (steps.length >= 4) {
        // Step 1 is always accessible (index 0)

        // Step 2 (Upload data) - index 1 - always accessible
        // We want users to always be able to upload data

        // Step 3 (Set criteria) - index 2 - requires data
        const step3 = steps[2];
        if (step3) {
            const step3Link = step3.querySelector('.step-trigger');
            if (step3Link) {
                if (!hasData) {
                    step3Link.onclick = function (e) { e.preventDefault(); return false; };
                    step3Link.style.cursor = 'not-allowed';
                    step3Link.style.opacity = '0.5';
                    step3Link.style.pointerEvents = 'none';
                } else {
                    step3Link.onclick = null;
                    step3Link.style.cursor = 'pointer';
                    step3Link.style.opacity = '1';
                    step3Link.style.pointerEvents = 'auto';
                }
            }
        }

        // Step 4 (Analyze) - index 3 - requires params
        const step4 = steps[3];
        if (step4) {
            const step4Link = step4.querySelector('.step-trigger');
            if (step4Link) {
                if (!hasParams || !hasData) {
                    step4Link.onclick = function (e) { e.preventDefault(); return false; };
                    step4Link.style.cursor = 'not-allowed';
                    step4Link.style.opacity = '0.5';
                    step4Link.style.pointerEvents = 'none';
                } else {
                    step4Link.onclick = null;
                    step4Link.style.cursor = 'pointer';
                    step4Link.style.opacity = '1';
                    step4Link.style.pointerEvents = 'auto';
                }
            }
        }
    }
}

// Run on page load and whenever session storage changes
document.addEventListener('DOMContentLoaded', function () {
    updateStepperLinks();

    // Update stepper links periodically to catch storage changes
    setInterval(updateStepperLinks, 500);
});

// Also run immediately in case DOM is already loaded
updateStepperLinks();