import 'package:flutter/material.dart';
import '../models/document_filter.dart';

class FilterSelector extends StatelessWidget {
  final DocumentFilter selectedFilter;
  final Function(DocumentFilter) onFilterSelected;

  const FilterSelector({
    super.key,
    required this.selectedFilter,
    required this.onFilterSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 100,
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        children: DocumentFilter.values.map((filter) {
          final isSelected = filter == selectedFilter;
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: GestureDetector(
              onTap: () => onFilterSelected(filter),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 60,
                    height: 60,
                    decoration: BoxDecoration(
                      color: isSelected
                          ? Colors.white.withOpacity(0.2)
                          : Colors.white.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(15),
                      border: Border.all(
                        color: isSelected ? Colors.white : Colors.white30,
                        width: 2,
                      ),
                    ),
                    child: Icon(
                      _getFilterIcon(filter),
                      color: Colors.white,
                      size: 28,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _getFilterName(filter),
                    style: TextStyle(
                      color: isSelected ? Colors.white : Colors.white70,
                      fontSize: 12,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  IconData _getFilterIcon(DocumentFilter filter) {
    switch (filter) {
      case DocumentFilter.original:
        return Icons.image;
      case DocumentFilter.grayscale:
        return Icons.filter_b_and_w;
      case DocumentFilter.blackWhite:
        return Icons.contrast;
      case DocumentFilter.enhance:
        return Icons.auto_awesome;
      case DocumentFilter.sharp:
        return Icons.details;
    }
  }

  String _getFilterName(DocumentFilter filter) {
    switch (filter) {
      case DocumentFilter.original:
        return 'Original';
      case DocumentFilter.grayscale:
        return 'Grayscale';
      case DocumentFilter.blackWhite:
        return 'B&W';
      case DocumentFilter.enhance:
        return 'Enhance';
      case DocumentFilter.sharp:
        return 'Sharp';
    }
  }
}