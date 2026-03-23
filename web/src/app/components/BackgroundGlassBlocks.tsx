import { memo } from "react";
import { motion, useReducedMotion } from "motion/react";

const colorBlocks = [
  {
    className:
      "left-[-14%] top-[2%] h-[20rem] w-[26rem] md:h-[28rem] md:w-[34rem]",
    tintClassName: "bg-blue-200/34",
    blurClassName: "blur-[68px] md:blur-[88px]",
    animation: {
      x: ["0%", "8%", "-5%", "0%"],
      y: ["0%", "-5%", "7%", "0%"],
      scale: [1, 1.04, 0.98, 1],
      opacity: [0.26, 0.4, 0.32, 0.26],
    },
    duration: 24,
  },
  {
    className:
      "right-[-10%] top-[18%] h-[18rem] w-[22rem] md:h-[24rem] md:w-[30rem]",
    tintClassName: "bg-cyan-200/28",
    blurClassName: "blur-[64px] md:blur-[84px]",
    animation: {
      x: ["0%", "-10%", "6%", "0%"],
      y: ["0%", "8%", "-6%", "0%"],
      scale: [1, 1.05, 0.97, 1],
      opacity: [0.22, 0.34, 0.26, 0.22],
    },
    duration: 22,
  },
  {
    className:
      "left-[18%] bottom-[-10%] h-[18rem] w-[24rem] md:h-[24rem] md:w-[32rem]",
    tintClassName: "bg-amber-100/24",
    blurClassName: "blur-[60px] md:blur-[80px]",
    animation: {
      x: ["0%", "9%", "-8%", "0%"],
      y: ["0%", "-8%", "6%", "0%"],
      scale: [1, 1.04, 0.98, 1],
      opacity: [0.18, 0.28, 0.22, 0.18],
    },
    duration: 26,
  },
];

export const BackgroundGlassBlocks = memo(function BackgroundGlassBlocks() {
  const reduceMotion = useReducedMotion();

  return (
    <div className="absolute inset-0 overflow-hidden">
      {colorBlocks.map((block) => (
        <motion.div
          key={block.className}
          className={`absolute rounded-[46%] transform-gpu ${block.className}`}
          animate={reduceMotion ? undefined : block.animation}
          transition={{
            duration: block.duration,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <div className={`absolute inset-0 rounded-[inherit] ${block.blurClassName} ${block.tintClassName}`} />
          <div className="absolute inset-[18%] rounded-[inherit] bg-white/10 blur-[28px]" />
        </motion.div>
      ))}
    </div>
  );
});
