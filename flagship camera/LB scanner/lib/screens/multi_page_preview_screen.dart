import 'dart:io';
import 'package:flutter/material.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:path_provider/path_provider.dart';
import 'package:open_file/open_file.dart';
import '../services/document_manager.dart';
import 'camera_screen.dart';
import 'edit_screen.dart';

class MultiPagePreviewScreen extends StatefulWidget {
  const MultiPagePreviewScreen({super.key});

  @override
  State<MultiPagePreviewScreen> createState() => _MultiPagePreviewScreenState();
}

class _MultiPagePreviewScreenState extends State<MultiPagePreviewScreen> {
  final DocumentManager _documentManager = DocumentManager();
  bool _isGeneratingPdf = false;

  @override
  Widget build(BuildContext context) {
    final session = _documentManager.currentSession;
    final pages = session?.pages ?? [];

    return WillPopScope(
      onWillPop: () async {
        final shouldPop = await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Discard Document?'),
            content: const Text('Are you sure you want to discard this document?'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Cancel'),
              ),
              TextButton(
                onPressed: () {
                  _documentManager.clearCurrentSession();
                  Navigator.pop(context, true);
                },
                child: const Text('Discard'),
              ),
            ],
          ),
        );
        return shouldPop ?? false;
      },
      child: Scaffold(
        appBar: AppBar(
          title: Text('Document (${pages.length} pages)'),
          actions: [
            if (pages.isNotEmpty)
              IconButton(
                icon: const Icon(Icons.picture_as_pdf),
                onPressed: _isGeneratingPdf ? null : _generatePdf,
              ),
          ],
        ),
        body: pages.isEmpty
            ? Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.document_scanner_outlined,
                      size: 100,
                      color: Theme.of(context).colorScheme.onSurface.withOpacity(0.3),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'No pages added yet',
                      style: TextStyle(fontSize: 18),
                    ),
                    const SizedBox(height: 8),
                    ElevatedButton.icon(
                      onPressed: _addPage,
                      icon: const Icon(Icons.add_a_photo),
                      label: const Text('Add First Page'),
                    ),
                  ],
                ),
              )
            : Column(
                children: [
                  Expanded(
                    child: ReorderableListView.builder(
                      onReorder: (oldIndex, newIndex) {
                        setState(() {
                          if (newIndex > oldIndex) {
                            newIndex -= 1;
                          }
                          final item = pages.removeAt(oldIndex);
                          pages.insert(newIndex, item);
                        });
                      },
                      itemCount: pages.length,
                      itemBuilder: (context, index) {
                        final page = pages[index];
                        return Card(
                          key: ValueKey(page.id),
                          margin: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 8,
                          ),
                          child: ListTile(
                            leading: ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              child: Image.file(
                                File(page.displayPath),
                                width: 60,
                                height: 80,
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) {
                                  return Container(
                                    width: 60,
                                    height: 80,
                                    color: Colors.grey[300],
                                    child: const Icon(Icons.error),
                                  );
                                },
                              ),
                            ),
                            title: Text('Page ${index + 1}'),
                            subtitle: Text(
                              'Tap to edit • Hold and drag to reorder',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                            trailing: IconButton(
                              icon: const Icon(Icons.delete),
                              onPressed: () => _deletePage(index),
                            ),
                            onTap: () => _editPage(index),
                          ),
                        );
                      },
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.surface,
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 4,
                          offset: const Offset(0, -2),
                        ),
                      ],
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: _addPage,
                            icon: const Icon(Icons.add_a_photo),
                            label: const Text('Add Page'),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: pages.isEmpty || _isGeneratingPdf 
                                ? null 
                                : _generatePdf,
                            icon: _isGeneratingPdf
                                ? const SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                    ),
                                  )
                                : const Icon(Icons.save),
                            label: Text(_isGeneratingPdf ? 'Generating...' : 'Save PDF'),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  void _addPage() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const CameraScreen(isAddingToDocument: true),
      ),
    );
  }

  void _editPage(int index) {
    final page = _documentManager.currentSession!.pages[index];
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => EditScreen(
          imagePath: page.displayPath,
          pageIndex: index,
        ),
      ),
    );
  }

  void _deletePage(int index) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Page?'),
        content: Text('Are you sure you want to delete page ${index + 1}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              setState(() {
                _documentManager.removePage(index);
              });
              Navigator.pop(context);
            },
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  Future<void> _generatePdf() async {
    final pages = _documentManager.currentSession?.pages ?? [];
    if (pages.isEmpty) return;

    setState(() {
      _isGeneratingPdf = true;
    });

    try {
      final pdf = pw.Document();

      for (final page in pages) {
        final imageFile = File(page.displayPath);
        if (await imageFile.exists()) {
          final imageBytes = await imageFile.readAsBytes();
          final pdfImage = pw.MemoryImage(imageBytes);

          pdf.addPage(
            pw.Page(
              pageFormat: PdfPageFormat.a4,
              build: (pw.Context context) {
                return pw.Center(
                  child: pw.Image(pdfImage),
                );
              },
            ),
          );
        }
      }

      final output = await getApplicationDocumentsDirectory();
      final fileName = 'document_${DateTime.now().millisecondsSinceEpoch}.pdf';
      final file = File('${output.path}/$fileName');
      await file.writeAsBytes(await pdf.save());

      _documentManager.saveSession(file.path);

      await OpenFile.open(file.path);

      if (mounted) {
        Navigator.of(context).popUntil((route) => route.isFirst);
      }
    } catch (e) {
      debugPrint('Error generating PDF: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error generating PDF: $e')),
        );
      }
    } finally {
      setState(() {
        _isGeneratingPdf = false;
      });
    }
  }
}