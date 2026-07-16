import {
  Brain,
  Sparkles,
  CheckCircle2,
} from "lucide-react";

function AiConfidenceCard({ confidence }) {
  const percentage = Math.round((confidence || 0) * 100);

  const radius = 72;
  const circumference = 2 * Math.PI * radius;

  const progress =
    circumference -
    (percentage / 100) * circumference;

  return (
    <div className="bg-gradient-to-br from-indigo-600 via-blue-600 to-cyan-500 rounded-3xl shadow-xl text-white overflow-hidden">

      <div className="p-8">

        <div className="flex items-center gap-3 mb-6">

          <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">

            <Brain size={26} />

          </div>

          <div>

            <p className="text-sm uppercase tracking-wider text-blue-100">

              Artificial Intelligence

            </p>

            <h2 className="text-2xl font-bold">

              Confidence Score

            </h2>

          </div>

        </div>

        <div className="flex justify-center my-8">

          <div className="relative">

            <svg
              width="180"
              height="180"
              className="-rotate-90"
            >

              <circle
                cx="90"
                cy="90"
                r={radius}
                fill="transparent"
                stroke="rgba(255,255,255,.15)"
                strokeWidth="14"
              />

              <circle
                cx="90"
                cy="90"
                r={radius}
                fill="transparent"
                stroke="white"
                strokeWidth="14"
                strokeDasharray={circumference}
                strokeDashoffset={progress}
                strokeLinecap="round"
                style={{
                  transition: "all .8s ease",
                }}
              />

            </svg>

            <div className="absolute inset-0 flex flex-col items-center justify-center">

              <h1 className="text-5xl font-bold">

                {percentage}%

              </h1>

              <p className="text-blue-100 text-sm mt-1">

                Confidence

              </p>

            </div>

          </div>

        </div>

        <div className="grid grid-cols-2 gap-4">

          <div className="bg-white/15 rounded-xl p-4">

            <div className="flex items-center gap-2 mb-2">

              <Sparkles size={18} />

              <span className="font-semibold">

                AI Status

              </span>

            </div>

            <p className="text-sm text-blue-100">

              Models operating normally

            </p>

          </div>

          <div className="bg-white/15 rounded-xl p-4">

            <div className="flex items-center gap-2 mb-2">

              <CheckCircle2 size={18} />

              <span className="font-semibold">

                Accuracy

              </span>

            </div>

            <p className="text-sm text-blue-100">

              Excellent predictions

            </p>

          </div>

        </div>

      </div>

    </div>
  );
}

export default AiConfidenceCard;