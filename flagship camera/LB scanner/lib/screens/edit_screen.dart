import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image/image.dart' as img;
import 'package:path_provider/path_provider.dart';
import '../widgets/filter_selector.dart';
import '../widgets/adjustment_slider.dart';
import '../models/document_filter.dart';
import '../models/document_model.dart';
import '../services/document_manager.dart';
import 'multi_page_preview_screen.dart';

class EditScreen extends StatefulWidget {
  final String imagePath;
  final int? pageIndex;

  const EditScreen({
    super.key, 
    required this.imagePath,
    this.pageIndex,
  });

  @override
  State<EditScreen> createState() => _EditScreenState();
}

class _EditScreenState extends State<EditScreen> {
  img.Image? _originalImage;
  img.Image? _editedImage;
  Uint8List? _displayBytes;
  bool _isLoading = true;
  bool _isProcessing = false;
  DocumentFilter _selectedFilter = DocumentFilter.original;
  double _brightness = 0.0;
  double _contrast = 1.0;
  int _selectedTab = 0;
  final DocumentManager _documentManager = DocumentManager();

  @override
  void initState() {
    super.initState();
    _loadImage();
  }

  Future<void> _loadImage() async {
    try {
      final bytes = await File(widget.imagePath).readAsBytes();
      final image = img.decodeImage(bytes);
      
      if (image != null) {
        setState(() {
          _originalImage = image;
          _editedImage = img.Image.from(image);
          _displayBytes = bytes;
          _isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('Error loading image: $e');
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _applyFilter(DocumentFilter filter) async {
    if (_originalImage == null || _isProcessing) return;

    setState(() {
      _selectedFilter = filter;
      _isProcessing = true;
    });

    try {
      // Process in isolate for better performance
      final processed = await _processImage(filter);
      
      if (processed != null) {
        final bytes = img.encodePng(processed);
        setState(() {
          _editedImage = processed;
          _displayBytes = Uint8List.fromList(bytes);
          _isProcessing = false;
        });
      }
    } catch (e) {
      debugPrint('Error applying filter: $e');
      setState(() {
        _isProcessing = false;
      });
    }
  }

  Future<img.Image?> _processImage(DocumentFilter filter) async {
    if (_originalImage == null) return null;

    img.Image processed = img.Image.from(_originalImage!);
    
    try {
      switch (filter) {
        case DocumentFilter.original:
          // Return original
          break;
        case DocumentFilter.grayscale:
          processed = img.grayscale(processed);
          break;
        case DocumentFilter.blackWhite:
          processed = img.grayscale(processed);
          // Apply threshold
          for (int y = 0; y < processed.height; y++) {
            for (int x = 0; x < processed.width; x++) {
              final pixel = processed.getPixel(x, y);
              final luminance = img.getLuminance(pixel);
              final newColor = luminance > 128 ? 255 : 0;
              processed.setPixelRgba(x, y, newColor, newColor, newColor, 255);
            }
          }
          break;
        case DocumentFilter.enhance:
          // Enhance document readability
          processed = img.adjustColor(processed, contrast: 1.5);
          processed = img.adjustColor(processed, brightness: 20);
          break;
        case DocumentFilter.sharp:
          // Apply simple sharpening without complex pixel manipulation
          // Using convolution filter for sharpening
          final sharpenFilter = [
            0, -1, 0,
            -1, 5, -1,
            0, -1, 0,
          ];
          processed = img.convolution(processed, filter: sharpenFilter, div: 1, offset: 0);
          break;
      }

      // Apply brightness and contrast adjustments
      if (_brightness != 0.0) {
        processed = img.adjustColor(processed, brightness: (_brightness * 100).toInt());
      }
      if (_contrast != 1.0) {
        processed = img.adjustColor(processed, contrast: _contrast);
      }

      return processed;
    } catch (e) {
      debugPrint('Error in image processing: $e');
      return _originalImage;
    }
  }

  Future<void> _saveAndContinue() async {
    if (_editedImage == null) return;

    setState(() {
      _isLoading = true;
    });

    try {
      // Save edited image
      final tempDir = await getTemporaryDirectory();
      final fileName = 'edited_${DateTime.now().millisecondsSinceEpoch}.png';
      final file = File('${tempDir.path}/$fileName');
      await file.writeAsBytes(img.encodePng(_editedImage!));

      if (widget.pageIndex != null) {
        // Update existing page
        _documentManager.updatePage(widget.pageIndex!, file.path);
      } else {
        // Add new page
        _documentManager.addPage(ScannedDocument(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          imagePath: widget.imagePath,
          editedImagePath: file.path,
          createdAt: DateTime.now(),
        ));
      }

      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => const MultiPagePreviewScreen(),
          ),
        );
      }
    } catch (e) {
      debugPrint('Error saving: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _cropImage() async {
    // Simple crop implementation
    if (_editedImage == null) return;
    
    // Show a dialog or a new screen for cropping
    // For now, just show a snackbar
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Crop feature coming soon!')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black,
        title: const Text('Edit Document'),
        actions: [
          IconButton(
            icon: const Icon(Icons.rotate_right),
            onPressed: _editedImage == null ? null : () async {
              setState(() => _isProcessing = true);
              final rotated = img.copyRotate(_editedImage!, angle: 90);
              final bytes = img.encodePng(rotated);
              setState(() {
                _editedImage = rotated;
                _displayBytes = Uint8List.fromList(bytes);
                _isProcessing = false;
              });
            },
          ),
          IconButton(
            icon: const Icon(Icons.crop),
            onPressed: _cropImage,
          ),
          IconButton(
            icon: const Icon(Icons.check),
            onPressed: _isLoading || _isProcessing ? null : _saveAndContinue,
          ),
        ],
      ),
      body: Stack(
        children: [
          // Image Preview
          Positioned.fill(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _displayBytes == null
                    ? const Center(
                        child: Text(
                          'Failed to load image',
                          style: TextStyle(color: Colors.white),
                        ),
                      )
                    : InteractiveViewer(
                        child: Center(
                          child: Image.memory(
                            _displayBytes!,
                            fit: BoxFit.contain,
                          ),
                        ),
                      ),
          ),
          
          // Processing indicator
          if (_isProcessing)
            Container(
              color: Colors.black54,
              child: const Center(
                child: CircularProgressIndicator(),
              ),
            ),
          
          // Bottom Controls
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.9),
                borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Tab Selector
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        _buildTab('Filters', 0, Icons.filter),
                        _buildTab('Adjust', 1, Icons.tune),
                        _buildTab('Effects', 2, Icons.auto_awesome),
                      ],
                    ),
                  ),
                  
                  // Content based on selected tab
                  AnimatedSwitcher(
                    duration: const Duration(milliseconds: 300),
                    child: _buildTabContent(),
                  ),
                  
                  const SizedBox(height: 20),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTab(String title, int index, IconData icon) {
    final isSelected = _selectedTab == index;
    return GestureDetector(
      onTap: () => setState(() => _selectedTab = index),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white.withOpacity(0.2) : Colors.transparent,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Row(
          children: [
            Icon(
              icon,
              color: isSelected ? Colors.white : Colors.white60,
              size: 20,
            ),
            const SizedBox(width: 8),
            Text(
              title,
              style: TextStyle(
                color: isSelected ? Colors.white : Colors.white60,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTabContent() {
    switch (_selectedTab) {
      case 0:
        return FilterSelector(
          selectedFilter: _selectedFilter,
          onFilterSelected: _applyFilter,
        );
      case 1:
        return Column(
          children: [
            AdjustmentSlider(
              label: 'Brightness',
              value: _brightness,
              min: -1.0,
              max: 1.0,
              onChanged: (value) {
                setState(() => _brightness = value);
                _applyFilter(_selectedFilter);
              },
            ),
            AdjustmentSlider(
              label: 'Contrast',
              value: _contrast,
              min: 0.5,
              max: 2.0,
              onChanged: (value) {
                setState(() => _contrast = value);
                _applyFilter(_selectedFilter);
              },
            ),
          ],
        );
      case 2:
        return const Center(
          child: Padding(
            padding: EdgeInsets.all(20),
            child: Text(
              'More effects coming soon!',
              style: TextStyle(color: Colors.white60),
            ),
          ),
        );
      default:
        return const SizedBox.shrink();
    }
  }
}