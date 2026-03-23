import { memo } from "react";
import { motion, useReducedMotion } from "motion/react";

const colorBlocks = [
  {
    className:
      "left-[-10%] top-[6%] h-[22rem] w-[28rem] md:h-[30rem] md:w-[38rem] rounded-[44%]",
    tintClassName: "bg-blue-200/40",
    blurClassName: "blur-[84px] md:blur-[110px]",
    animation: {
      x: ["0%", "12%", "-6%", "0%"],
      y: ["0%", "-8%", "10%", "0%"],
      rotate: ["-12deg", "-7deg", "-14deg", "-12deg"],
      scale: [1, 1.08, 0.96, 1],
      opacity: [0.34, 0.52, 0.4, 0.34],
    },
    duration: 28,
  },
  {
    className:
      "right-[-8%] top-[14%] h-[18rem] w-[24rem] md:h-[26rem] md:w-[34rem] rounded-[40%]",
    tintClassName: "bg-cyan-200/34",
    blurClassName: "blur-[78px] md:blur-[100px]",
    animation: {
      x: ["0%", "-14%", "8%", "0%"],
      y: ["0%", "10%", "-7%", "0%"],
      rotate: ["10deg", "6deg", "12deg", "10deg"],
      scale: [1, 1.06, 0.95, 1],
      opacity: [0.28, 0.42, 0.34, 0.28],
    },
    duration: 25,
  },
  {
    className:
      "left-[16%] bottom-[-8%] h-[20rem] w-[26rem] md:h-[28rem] md:w-[36rem] rounded-[42%]",
    tintClassName: "bg-sky-100/30",
    blurClassName: "blur-[82px] md:blur-[108px]",
    animation: {
      x: ["0%", "10%", "-10%", "0%"],
      y: ["0%", "-10%", "8%", "0%"],
      rotate: ["14deg", "9deg", "16deg", "14deg"],
      scale: [1, 1.07, 0.94, 1],
      opacity: [0.24, 0.38, 0.3, 0.24],
    },
    duration: 31,
  },
  {
    className:
      "right-[18%] bottom-[2%] h-[16rem] w-[22rem] md:h-[24rem] md:w-[30rem] rounded-[38%]",
    tintClassName: "bg-amber-100/30",
    blurClassName: "blur-[74px] md:blur-[96px]",
    animation: {
      x: ["0%", "-10%", "8%", "0%"],
      y: ["0%", "12%", "-8%", "0%"],
      rotate: ["-10deg", "-6deg", "-12deg", "-10deg"],
      scale: [1, 1.05, 0.95, 1],
      opacity: [0.2, 0.32, 0.24, 0.2],
    },
    duration: 29,
  },
  {
    className:
      "left-[40%] top-[28%] h-[14rem] w-[14rem] md:h-[18rem] md:w-[18rem] rounded-full",
    tintClassName: "bg-white/38",
    blurClassName: "blur-[62px] md:blur-[84px]",
    animation: {
      x: ["0%", "16%", "-12%", "0%"],
      y: ["0%", "-14%", "10%", "0%"],
      scale: [1, 1.12, 0.92, 1],
      opacity: [0.22, 0.36, 0.26, 0.22],
    },
    duration: 22,
  },
];

export const BackgroundGlassBlocks = memo(function BackgroundGlassBlocks() {
  const reduceMotion = useReducedMotion();

  return (
    <div className="absolute inset-0 overflow-hidden">
      {colorBlocks.map((block) => (
        <motion.div
          key={block.className}
          className={`absolute ${block.className}`}
          animate={reduceMotion ? undefined : block.animation}
          transition={{
            duration: block.duration,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <div className={`absolute inset-0 ${block.blurClassName} ${block.tintClassName}`} />
          <div className="absolute inset-[18%] rounded-[inherit] border border-white/18 bg-white/10 backdrop-blur-3xl" />
        </motion.div>
      ))}
    </div>
  );
});
