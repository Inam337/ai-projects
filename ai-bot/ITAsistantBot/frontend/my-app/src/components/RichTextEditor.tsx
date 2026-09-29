import { useEffect, useRef, useState } from 'react'
import { CKEditor } from '@ckeditor/ckeditor5-react'
import type { Editor as CKEditorType } from 'ckeditor5'

interface RichTextEditorProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  rows?: number
}

export const RichTextEditor = ({ value, onChange, placeholder }: RichTextEditorProps) => {
  const [Editor, setEditor] = useState<unknown>(null)
  const [isLoading, setIsLoading] = useState(true)
  const editorRef = useRef<CKEditorType | null>(null)

  useEffect(() => {
    // Try to load ClassicEditor from pre-built package
    const loadEditor = async () => {
      try {
        // First try: @ckeditor/ckeditor5-build-classic
        const classicBuild = await import('@ckeditor/ckeditor5-build-classic')
        // Handle both default export and named export
        const EditorClass = classicBuild.default || classicBuild.ClassicEditor || classicBuild
        setEditor(() => EditorClass)
        setIsLoading(false)
      } catch (err1) {
        console.warn('Failed to load @ckeditor/ckeditor5-build-classic, trying alternative:', err1)
        try {
          // Second try: Create a minimal editor from ckeditor5 package
          const ckeditor5 = await import('ckeditor5')
          const { ClassicEditor, Essentials, Paragraph, Bold, Italic, Heading, List, Link, BlockQuote } = ckeditor5
          
          // Define CustomEditor outside the try block to avoid inline class declaration
          const CustomEditorClass = class extends ClassicEditor {
            static builtinPlugins = [Essentials, Paragraph, Bold, Italic, Heading, List, Link, BlockQuote]
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            static defaultConfig: any = {
              toolbar: ['heading', '|', 'bold', 'italic', '|', 'bulletedList', 'numberedList', '|', 'link', 'blockQuote', '|', 'undo', 'redo'],
              heading: {
                options: [
                  { model: 'paragraph', title: 'Paragraph', class: 'ck-heading_paragraph' },
                  { model: 'heading1', view: 'h1', title: 'Heading 1', class: 'ck-heading_heading1' },
                  { model: 'heading2', view: 'h2', title: 'Heading 2', class: 'ck-heading_heading2' }
                ]
              }
            }
          }
          
          setEditor(() => CustomEditorClass)
          setIsLoading(false)
        } catch (err2) {
          console.error('Failed to load CKEditor:', err2)
          setIsLoading(false)
        }
      }
    }
    
    loadEditor()
  }, [])

  if (isLoading) {
    return (
      <div className="border-2 border-gray-300 rounded-lg p-8 text-center bg-white">
        <div className="animate-spin h-8 w-8 border-4 border-purple-600 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-gray-500 text-sm">Loading editor...</p>
      </div>
    )
  }

  if (!Editor) {
    // Fallback to enhanced textarea
    return (
      <div className="border-2 border-gray-300 rounded-lg focus-within:border-purple-500 focus-within:ring-2 focus-within:ring-purple-200 transition-all bg-white">
        <div className="p-2 border-b border-gray-200 flex gap-1 flex-wrap">
          <button
            type="button"
            onClick={() => {
              const textarea = document.querySelector('textarea[data-rich-text]') as HTMLTextAreaElement
              if (textarea) {
                const start = textarea.selectionStart
                const end = textarea.selectionEnd
                const text = value
                const before = text.substring(0, start)
                const selected = text.substring(start, end)
                const after = text.substring(end)
                onChange(before + '**' + selected + '**' + after)
                setTimeout(() => {
                  textarea.focus()
                  textarea.setSelectionRange(start + 2, end + 2)
                }, 0)
              }
            }}
            className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
            title="Bold"
          >
            <strong>B</strong>
          </button>
          <button
            type="button"
            onClick={() => {
              const textarea = document.querySelector('textarea[data-rich-text]') as HTMLTextAreaElement
              if (textarea) {
                const start = textarea.selectionStart
                const end = textarea.selectionEnd
                const text = value
                const before = text.substring(0, start)
                const selected = text.substring(start, end)
                const after = text.substring(end)
                onChange(before + '*' + selected + '*' + after)
                setTimeout(() => {
                  textarea.focus()
                  textarea.setSelectionRange(start + 1, end + 1)
                }, 0)
              }
            }}
            className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
            title="Italic"
          >
            <em>I</em>
          </button>
        </div>
        <textarea
          data-rich-text
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder || 'Format: 1) First step. 2) Second step. 3) Third step.'}
          className="w-full px-4 py-3 border-0 rounded-lg focus:outline-none font-mono text-sm transition-all resize-none"
          rows={6}
          required
        />
        <p className="text-xs text-gray-500 px-4 pb-2">Enhanced text editor (CKEditor not available)</p>
      </div>
    )
  }

  return (
    <div className="relative">
      <div className="mb-2">
        <p className="text-xs text-gray-500">Use the editor toolbar for rich text formatting. Format steps as: number) step description</p>
      </div>
      <div className="border-2 border-gray-300 rounded-lg focus-within:border-purple-500 focus-within:ring-2 focus-within:ring-purple-200 transition-all overflow-hidden bg-white">
        <style>{`
          .ck-editor__editable {
            min-height: 200px;
            max-height: 400px;
            overflow-y: auto;
            padding: 1rem;
          }
          .ck-editor__editable_inline {
            min-height: 200px;
            max-height: 400px;
            overflow-y: auto;
            padding: 1rem;
          }
          .ck-content {
            font-size: 14px;
            line-height: 1.6;
          }
          .ck.ck-editor {
            border: none;
          }
          .ck.ck-toolbar {
            border: none;
            border-bottom: 1px solid #e5e7eb;
            background: #f9fafb;
          }
          .ck.ck-editor__main > .ck-editor__editable {
            border: none;
          }
          .ck.ck-button {
            color: #374151;
          }
          .ck.ck-button:hover {
            background: #e5e7eb;
          }
        `}</style>
        <CKEditor
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          editor={Editor as any}
          config={{
            placeholder: placeholder || 'Format: 1) First step. 2) Second step. 3) Third step.',
            toolbar: {
              items: [
                'heading',
                '|',
                'bold',
                'italic',
                'link',
                'bulletedList',
                'numberedList',
                '|',
                'outdent',
                'indent',
                '|',
                'blockQuote',
                'insertTable',
                '|',
                'undo',
                'redo'
              ],
              shouldNotGroupWhenFull: true
            },
            heading: {
              options: [
                { model: 'paragraph', title: 'Paragraph', class: 'ck-heading_paragraph' },
                { model: 'heading1', view: 'h1', title: 'Heading 1', class: 'ck-heading_heading1' },
                { model: 'heading2', view: 'h2', title: 'Heading 2', class: 'ck-heading_heading2' },
                { model: 'heading3', view: 'h3', title: 'Heading 3', class: 'ck-heading_heading3' }
              ]
            },
            link: {
              decorators: {
                openInNewTab: {
                  mode: 'manual',
                  label: 'Open in a new tab',
                  attributes: {
                    target: '_blank',
                    rel: 'noopener noreferrer'
                  }
                }
              }
            },
            table: {
              contentToolbar: ['tableColumn', 'tableRow', 'mergeTableCells']
            }
          }}
          data={value || ''}
          onReady={(editor) => {
            editorRef.current = editor
          }}
          onChange={(_event, editor) => {
            const data = editor.getData()
            onChange(data)
          }}
        />
      </div>
    </div>
  )
}
