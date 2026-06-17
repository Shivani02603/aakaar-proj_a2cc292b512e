'use client'

import { useState } from 'react'
import { Inter } from 'next/font/google'
import { useRouter } from 'next/navigation'
import { uploadFile } from '@/lib/api'

const inter = Inter({ subsets: ['latin'] })

interface FormData {
  session_id: string
  file: File | null
}

interface FormErrors {
  session_id?: string
  file?: string
}

export default function NewUploadPage() {
  const router = useRouter()
  const [formData, setFormData] = useState<FormData>({
    session_id: '',
    file: null
  })
  const [errors, setErrors] = useState<FormErrors>({})
  const [loading, setLoading] = useState<boolean>(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    if (!formData.session_id.trim()) {
      newErrors.session_id = 'Session ID is required'
    } else if (isNaN(Number(formData.session_id))) {
      newErrors.session_id = 'Session ID must be a number'
    }

    if (!formData.file) {
      newErrors.file = 'File is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }))
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    setFormData(prev => ({ ...prev, file }))
    if (errors.file) {
      setErrors(prev => ({ ...prev, file: undefined }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitError(null)

    if (!validateForm()) return

    try {
      setLoading(true)
      await uploadFile(Number(formData.session_id), formData.file!)
      router.push('/upload')
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Failed to upload file')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={`min-h-screen bg-gray-50 p-6 ${inter.className}`}>
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Upload New File</h1>
          <p className="text-gray-600 mt-2">Upload a document to be processed and indexed</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          {submitError && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700">{submitError}</p>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="space-y-6">
              <div>
                <label htmlFor="session_id" className="block text-sm font-medium text-gray-700 mb-1">
                  Session ID *
                </label>
                <input
                  type="text"
                  id="session_id"
                  name="session_id"
                  value={formData.session_id}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.session_id ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Enter session ID"
                />
                {errors.session_id && (
                  <p className="mt-1 text-sm text-red-600">{errors.session_id}</p>
                )}
              </div>

              <div>
                <label htmlFor="file" className="block text-sm font-medium text-gray-700 mb-1">
                  File *
                </label>
                <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                  <div className="space-y-1 text-center">
                    <svg
                      className="mx-auto h-12 w-12 text-gray-400"
                      stroke="currentColor"
                      fill="none"
                      viewBox="0 0 48 48"
                      aria-hidden="true"
                    >
                      <path
                        d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                        strokeWidth={2}
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    <div className="flex text-sm text-gray-600">
                      <label
                        htmlFor="file-upload"
                        className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                      >
                        <span>Upload a file</span>
                        <input
                          id="file-upload"
                          name="file"
                          type="file"
                          onChange={handleFileChange}
                          className="sr-only"
                        />
                      </label>
                      <p className="pl-1">or drag and drop</p>
                    </div>
                    <p className="text-xs text-gray-500">
                      PDF, Excel, Word, or text files up to 10MB
                    </p>
                  </div>
                </div>
                {formData.file && (
                  <p className="mt-2 text-sm text-gray-600">
                    Selected file: <span className="font-medium">{formData.file.name}</span>
                  </p>
                )}
                {errors.file && (
                  <p className="mt-1 text-sm text-red-600">{errors.file}</p>
                )}
              </div>
            </div>

            <div className="mt-8 flex items-center justify-between">
              <button
                type="button"
                onClick={() => router.back()}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Uploading...
                  </>
                ) : (
                  'Upload File'
                )}
              </button>
            </div>
          </form>
        </div>

        <div className="mt-8 text-sm text-gray-500">
          <p className="font-medium">Note:</p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li>Session ID must correspond to an existing session</li>
            <li>Uploaded files will be processed and indexed for AI queries</li>
            <li>Supported formats: PDF, Excel (.xlsx, .xls), Word (.docx), plain text</li>
            <li>Maximum file size: 10MB</li>
          </ul>
        </div>
      </div>
    </div>
  )
}