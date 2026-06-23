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
    <main className="min-h-screen bg-slate-50 text-slate-900 px-6 py-12">
      <div className="mx-auto max-w-4xl">
        <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-600">
          Campus Course-Schedule Optimizer
        </p>
        <h1 className="mb-6 text-3xl font-bold tracking-tight md:text-4xl">
          Generate your semester schedule
        </h1>

        <div className="mb-8 flex flex-wrap items-end gap-4 rounded-xl border bg-white p-5 shadow-sm">
          <div>
            <label className="block text-sm font-medium text-slate-700">
              Min Credits
            </label>
            <input
              type="number"
              value={minCredits}
              onChange={(e) => setMinCredits(Number(e.target.value))}
              className="mt-1 w-24 rounded-md border px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">
              Max Credits
            </label>
            <input
              type="number"
              value={maxCredits}
              onChange={(e) => setMaxCredits(Number(e.target.value))}
              className="mt-1 w-24 rounded-md border px-3 py-2"
            />
          </div>
          <button
            onClick={fetchSchedules}
            className="rounded-md bg-blue-600 px-5 py-2 font-semibold text-white hover:bg-blue-700"
          >
            Generate Schedules
          </button>
        </div>

        <div className="mb-8 rounded-xl border bg-white p-5 shadow-sm">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Describe your scheduling preferences
          </label>
          <textarea
            value={preferenceText}
            onChange={(e) => setPreferenceText(e.target.value)}
            placeholder="e.g. I want 15 credit hours, no Friday classes, nothing before 10am"
            className="w-full rounded-md border px-3 py-2 text-sm"
            rows={3}
          />
          <button
            onClick={parsePreferences}
            disabled={parsing || !preferenceText}
            className="mt-3 rounded-md bg-slate-700 px-5 py-2 font-semibold text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {parsing ? "Parsing..." : "Parse Preferences"}
          </button>

          {parsedPreferences && (
            <div className="mt-4 rounded-md bg-slate-50 p-3 text-sm">
              <p className="font-medium text-slate-700 mb-1">AI understood:</p>
              <pre className="whitespace-pre-wrap text-slate-600">
                {JSON.stringify(parsedPreferences, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {loading && <p className="text-slate-600">Generating schedules...</p>}
        {error && <p className="text-red-600">{error}</p>}

        <div className="grid gap-4 md:grid-cols-2">
          {schedules.map((schedule, i) => (
            <div key={i} className="rounded-xl border bg-white p-5 shadow-sm">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="font-semibold">Schedule {i + 1}</h2>
                <span className="text-sm text-slate-500">
                  Score: {schedule.score} · {schedule.total_credits} credits
                </span>
              </div>
              <ul className="space-y-2 text-sm">
                {schedule.courses.map((course, j) => (
                  <li key={j} className="border-b pb-2 last:border-0">
                    <div className="font-medium">
                      {course.course_code} — {course.course_name}
                    </div>
                    <div className="text-slate-600">
                      Section {course.section_number} · {course.professor} ·{" "}
                      {course.days_of_week} {course.start_time}–{course.end_time}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}

export default App;