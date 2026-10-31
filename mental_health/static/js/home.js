(() => {
    const gaugeProgress = document.querySelector(".gauge-progress");
    const gaugeMarker = document.querySelector(".gauge-marker");
    const scoreGauge = document.querySelector(".score-gauge");
    const gaugeValue = document.querySelector(".gauge-value");

    if (gaugeProgress && gaugeMarker && scoreGauge) {
        const pathLength = gaugeProgress.getTotalLength();
        const score = Math.min(
            100,
            Math.max(0, Number(gaugeProgress.dataset.score) || 0),
        );
        const targetValue = Number(gaugeValue?.dataset.score) || 0;
        const progress = { value: 0 };
        const animation = { value: 0 };

        gaugeProgress.style.strokeDasharray = `${pathLength}`;

        const drawGauge = () => {
            const distance = pathLength * progress.value;
            const point = gaugeProgress.getPointAtLength(distance);
            gaugeProgress.style.strokeDashoffset = `${pathLength - distance}`;
            gaugeMarker.setAttribute("cx", `${point.x}`);
            gaugeMarker.setAttribute("cy", `${point.y}`);
        };

        const setScoreValue = (value) => {
            if (gaugeValue) {
                gaugeValue.textContent = (targetValue * value).toFixed(1);
            }
        };

        drawGauge();
        setScoreValue(0);

        if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
            progress.value = score / 100;
            drawGauge();
            setScoreValue(1);
        } else if (window.gsap) {
            gsap.to(animation, {
                value: 1,
                duration: 1.6,
                delay: 0.35,
                ease: "power2.out",
                onUpdate: () => {
                    progress.value = (score / 100) * animation.value;
                    drawGauge();
                    setScoreValue(animation.value);
                },
            });
        } else {
            progress.value = score / 100;
            drawGauge();
            setScoreValue(1);
        }
    }

    const newResult = document.querySelector("[data-new-result]");
    if (newResult && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        window.setTimeout(() => {
            newResult.scrollIntoView({ behavior: "smooth", block: "center" });
        }, 450);
    }

    if (!window.gsap) {
        return;
    }

    const media = gsap.matchMedia();
    media.add(
        {
            motionAllowed: "(prefers-reduced-motion: no-preference)",
            motionReduced: "(prefers-reduced-motion: reduce)",
        },
        (context) => {
            const { motionAllowed } = context.conditions;

            if (!motionAllowed) {
                return;
            }

            const entrance = gsap.timeline({
                defaults: { ease: "power3.out" },
            });

            entrance
                .from(".topbar", { y: -18, opacity: 0, duration: 0.65 })
                .from(
                    ".hero-copy > *",
                    { y: 24, opacity: 0, duration: 0.7, stagger: 0.1 },
                    "-=0.3",
                )
                .from(
                    ".hero-art",
                    { y: 20, opacity: 0, scale: 0.96, duration: 0.9 },
                    "-=0.65",
                )
                .from(
                    ".checkin-card",
                    { y: 26, opacity: 0, duration: 0.8 },
                    "-=0.5",
                )
                .from(
                    ".field-wrap",
                    { y: 12, opacity: 0, duration: 0.45, stagger: 0.045 },
                    "-=0.35",
                );

            gsap.to(".art-card", {
                y: -7,
                rotation: -2,
                duration: 3.4,
                ease: "sine.inOut",
                repeat: -1,
                yoyo: true,
            });
            gsap.to(".art-sun", {
                scale: 1.06,
                duration: 2.8,
                ease: "sine.inOut",
                repeat: -1,
                yoyo: true,
            });
            gsap.to(".art-sparkle", {
                rotation: 24,
                scale: 1.12,
                duration: 2.2,
                ease: "sine.inOut",
                repeat: -1,
                yoyo: true,
                stagger: 0.4,
            });

            const submitButton = document.querySelector(".submit-button");
            submitButton?.addEventListener("pointerdown", () => {
                gsap.to(submitButton, {
                    scale: 0.97,
                    duration: 0.12,
                    yoyo: true,
                    repeat: 1,
                    ease: "power1.inOut",
                });
            });
        },
    );
})();