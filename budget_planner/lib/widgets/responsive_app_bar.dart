import 'package:flutter/material.dart';
import '../utils/responsive.dart';

class ResponsiveAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;

  const ResponsiveAppBar({required this.title, this.actions});

  @override
  Size get preferredSize => Size.fromHeight(kToolbarHeight);

  @override
  Widget build(BuildContext context) {
    final responsive = Responsive(context);
    
    return AppBar(
      title: Text(
        title,
        style: TextStyle(
          fontSize: responsive.responsiveValue(mobile: 18, tablet: 22),
        ),
      ),
      actions: actions,
    );
  }
}