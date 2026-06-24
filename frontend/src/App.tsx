import { useState } from "react";

interface CourseInSchedule {
  course_code: string;
  course_name: string;
  section_number: string;
  professor: string;
  days_of_week: string;
  start_time: string;
  end_time: string;
}

interface ScheduleResult {
  score: number;
  total_credits: number;
  courses: CourseInSchedule[];
}

interface ApiResponse {
  student_id: number;
  schedule_count: number;
  top_schedules: ScheduleResult[];
}

const ALL_DAYS = ["M", "T", "W", "R", "F"];

function dayStripColor(daysOfWeek: string, index: number) {
  const dayChar = ALL_DAYS[index];
  if (daysOfWeek.includes(dayChar)) {
    // Alternate between the two accent colors based on position for visual rhythm
    return index % 2 === 0 ? "bg-terracotta" : "bg-forest";
  }
  return "bg-parchment";
}

function App() {
  const [schedules, setSchedules] = useState<ScheduleResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [minCredits, setMinCredits] = useState(6);
  const [maxCredits, setMaxCredits] = useState(16);
  const [preferenceText, setPreferenceText] = useState("");
  const [parsedPreferences, setParsedPreferences] = useState<any>(null);
  const [parsing, setParsing] = useState(false);

  async function fetchSchedules() {
    setLoading(true);
    setError(null);
    try {
      let response;
      if (parsedPreferences && !parsedPreferences.error) {
        response = await fetch("http://127.0.0.1:8000/schedules/1/with-preferences", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(parsedPreferences),
        });
      } else {
        response = await fetch(
          `http://127.0.0.1:8000/schedules/1?min_credits=${minCredits}&max_credits=${maxCredits}`
        );
      }
      if (!response.ok) throw new Error("Failed to fetch schedules");
      const data: ApiResponse = await response.json();
      setSchedules(data.top_schedules);
    } catch (err) {
      setError("Could not load schedules. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  async function parsePreferences() {
    setParsing(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/ai/parse-preferences", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: preferenceText }),
      });
      const data = await response.json();
      setParsedPreferences(data);
    } catch (err) {
      setParsedPreferences({ error: "Could not reach AI service." });
    } finally {
      setParsing(false);
    }
  }

  return (
    <main className="min-h-screen bg-paper text-ink px-6 py-12 font-sans">
      <div className="mx-auto max-w-5xl">
        <p className="mb-1 font-serif text-xs uppercase tracking-[0.12em] text-stone">
          Campus Course-Schedule Optimizer
        </p>
        <h1 className="mb-8 font-serif text-3xl font-semibold tracking-tight md:text-4xl">
          Build your semester
        </h1>

        <div className="grid gap-6 md:grid-cols-[0.9fr_1.4fr]">
          {/* Left column: inputs */}
          <div className="flex flex-col gap-4">
            <div className="rounded-lg border border-parchment bg-white p-5">
              <p className="mb-3 border-b border-parchment pb-2 font-serif text-sm text-ink">
                Credit load
              </p>
              <div className="flex gap-3">
                <div className="flex-1">
                  <label className="text-[11px] uppercase tracking-wide text-stone">
                    Min
                  </label>
                  <input
                    type="number"
                    value={minCredits}
                    onChange={(e) => setMinCredits(Number(e.target.value))}
                    className="mt-1 w-full rounded-md border border-parchment px-3 py-2 text-sm"
                  />
                </div>
                <div className="flex-1">
                  <label className="text-[11px] uppercase tracking-wide text-stone">
                    Max
                  </label>
                  <input
                    type="number"
                    value={maxCredits}
                    onChange={(e) => setMaxCredits(Number(e.target.value))}
                    className="mt-1 w-full rounded-md border border-parchment px-3 py-2 text-sm"
                  />
                </div>
              </div>
              <button
                onClick={fetchSchedules}
                className="mt-4 w-full rounded-md bg-terracotta py-2.5 font-serif text-sm font-medium text-paper hover:opacity-90"
              >
                Generate schedules
              </button>
            </div>

            <div className="rounded-lg border border-parchment bg-white p-5">
              <p className="mb-3 border-b border-parchment pb-2 font-serif text-sm text-ink">
                Tell us what you want
              </p>
              <textarea
                value={preferenceText}
                onChange={(e) => setPreferenceText(e.target.value)}
                placeholder="No Friday classes, start after 10am"
                rows={3}
                className="w-full resize-none rounded-md border border-parchment px-3 py-2 text-sm"
              />
              <button
                onClick={parsePreferences}
                disabled={parsing || !preferenceText}
                className="mt-3 w-full rounded-md border border-forest py-2 font-serif text-sm font-medium text-forest hover:bg-forest hover:text-paper disabled:opacity-50"
              >
                {parsing ? "Parsing…" : "Parse preferences"}
              </button>

              {parsedPreferences && (
                <div className="mt-3 rounded-md bg-parchment/60 p-3 font-mono text-xs text-stone">
                  <pre className="whitespace-pre-wrap">
                    {JSON.stringify(parsedPreferences, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>

          {/* Right column: results */}
          <div>
            {loading && (
              <p className="font-serif text-sm text-stone">Generating schedules…</p>
            )}
            {error && (
              <p className="font-serif text-sm text-terracotta">{error}</p>
            )}
            {!loading && !error && schedules.length === 0 && (
              <p className="font-serif text-sm text-stone">
                No schedules matched those constraints. Try loosening your preferences or credit range.
              </p>
            )}

            <div className="grid gap-4 sm:grid-cols-2">
              {schedules.map((schedule, i) => (
                <div
                  key={i}
                  className="overflow-hidden rounded-lg border border-parchment bg-white"
                >
                  <div className="flex items-baseline justify-between px-4 pt-3 pb-2">
                    <h2 className="font-serif text-base font-semibold text-ink">
                      Schedule {i + 1}
                    </h2>
                    <span className="font-mono text-[11px] text-stone">
                      {schedule.score} pts · {schedule.total_credits}cr
                    </span>
                  </div>

                  <ul>
                    {schedule.courses.map((course, j) => (
                      <li key={j} className="border-t border-parchment/70 px-4 py-3">
                        <div className="mb-1.5 flex h-1 gap-0.5 overflow-hidden rounded-full">
                          {ALL_DAYS.map((_, idx) => (
                            <div
                              key={idx}
                              className={`flex-1 ${dayStripColor(course.days_of_week, idx)}`}
                            />
                          ))}
                        </div>
                        <p className="text-sm font-medium text-ink">
                          {course.course_code} — {course.course_name}
                        </p>
                        <p className="font-mono text-[11px] text-stone">
                          {course.days_of_week} {course.start_time}–{course.end_time} ·{" "}
                          {course.professor}
                        </p>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

export default App;