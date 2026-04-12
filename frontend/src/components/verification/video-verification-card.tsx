"use client";

import { useEffect, useState } from "react";

import { getMyVerification, reuploadIntroVideo, uploadIntroVideo } from "@/lib/api/verification";
import type { VerificationState } from "@/types/media";

export function VideoVerificationCard() {
  const [data, setData] = useState<VerificationState | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [duration, setDuration] = useState("20");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function loadVerification() {
    try {
      const result = await getMyVerification();
      setData(result);

      if (result.intro_video?.duration_seconds) {
        setDuration(String(result.intro_video.duration_seconds));
      }

      setError("");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load verification";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadVerification();
  }, []);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setNotice("");

    if (!selectedFile) {
      setError("Please select a video file.");
      return;
    }

    const durationValue = Number(duration);
    if (Number.isNaN(durationValue) || durationValue < 20 || durationValue > 30) {
      setError("Duration must be between 20 and 30 seconds.");
      return;
    }

    try {
      setSaving(true);

      const result = data?.intro_video
        ? await reuploadIntroVideo(selectedFile, durationValue)
        : await uploadIntroVideo(selectedFile, durationValue);

      setData(result);
      setSelectedFile(null);

      const input = document.getElementById("video-file-input") as HTMLInputElement | null;
      if (input) input.value = "";

      setNotice(data?.intro_video ? "Intro video reuploaded." : "Intro video uploaded.");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to save intro video";
      setError(msg);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-stone-900">Intro video verification</h3>
      <p className="mt-2 text-sm text-stone-600">
        Upload a real video file here. Keep it between 20 and 30 seconds.
      </p>

      {error ? (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      {notice ? (
        <div className="mt-4 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
          {notice}
        </div>
      ) : null}

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-stone-200 p-4">
          <p className="text-sm text-stone-500">Profile verification status</p>
          <p className="mt-2 text-lg font-semibold text-stone-900">
            {loading ? "Loading..." : data?.profile_verification_status ?? "not_started"}
          </p>
        </div>

        <div className="rounded-2xl border border-stone-200 p-4">
          <p className="text-sm text-stone-500">Current intro video status</p>
          <p className="mt-2 text-lg font-semibold text-stone-900">
            {loading ? "Loading..." : data?.intro_video?.verification_status ?? "not_uploaded"}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="mt-6 grid gap-4 md:grid-cols-2">
        <label className="text-sm md:col-span-2">
          <span className="mb-2 block font-medium text-stone-700">Select video</span>
          <input
            id="video-file-input"
            type="file"
            accept="video/mp4,video/webm,video/quicktime,video/x-m4v"
            onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
            className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
          />
        </label>

        <label className="text-sm">
          <span className="mb-2 block font-medium text-stone-700">Duration (seconds)</span>
          <input
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            type="number"
            min={20}
            max={30}
            className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
          />
        </label>

        <div className="flex items-end">
          <button
            type="submit"
            disabled={saving}
            className="rounded-xl bg-stone-900 px-5 py-3 text-sm font-medium text-white hover:bg-stone-800 disabled:opacity-60"
          >
            {saving ? "Uploading..." : data?.intro_video ? "Reupload video" : "Upload video"}
          </button>
        </div>
      </form>

      {data?.intro_video ? (
        <div className="mt-6 rounded-2xl border border-stone-200 p-4">
          <p className="text-sm text-stone-500">Current uploaded video</p>
          <video
            controls
            className="mt-3 w-full rounded-xl border border-stone-200"
            src={data.intro_video.video_url}
          />
        </div>
      ) : null}
    </div>
  );
}