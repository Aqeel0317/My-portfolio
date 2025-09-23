import 'package:flutter/material.dart';
import '../models/transaction.dart';
import '../utils/responsive.dart';
import 'add_transaction_screen.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';

class AllTransactionsScreen extends StatelessWidget {
  final List<Transaction> transactions;

  AllTransactionsScreen({required this.transactions});

  @override
  Widget build(BuildContext context) {
    final responsive = Responsive(context);
    return Scaffold(
      appBar: AppBar(
        title: Text('All Transactions'),
      ),
      body: ListView.builder(
        itemCount: transactions.length,
        itemBuilder: (context, index) {
          final transaction = transactions[index];
          return Card(
            margin: EdgeInsets.symmetric(
              horizontal: responsive.responsiveValue(mobile: 8, tablet: 24),
              vertical: 4,
            ),
            child: ListTile(
              contentPadding: EdgeInsets.symmetric(
                horizontal: responsive.responsiveValue(mobile: 12, tablet: 16),
                vertical: responsive.responsiveValue(mobile: 4, tablet: 8),
              ),
              leading: CircleAvatar(
                backgroundColor: _getCategoryColor(transaction.category).withOpacity(0.2),
                child: Icon(
                  _getCategoryIcon(transaction.category),
                  color: _getCategoryColor(transaction.category),
                ),
              ),
              title: Text(
                transaction.title,
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Text(
                DateFormat('MMM dd, yyyy').format(transaction.date),
              ),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '${transaction.isIncome ? '+' : '-'} \$${transaction.amount.toStringAsFixed(2)}',
                    style: TextStyle(
                      fontSize: responsive.responsiveValue(mobile: 14, tablet: 16),
                      fontWeight: FontWeight.bold,
                      color: transaction.isIncome ? Colors.green : Colors.red,
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.edit),
                    onPressed: () => Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => AddTransactionScreen(transaction: transaction)),
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.delete),
                    onPressed: () {
                      Provider.of<TransactionProvider>(context, listen: false)
                          .deleteTransaction(transaction.id!);
                      Navigator.pop(context); // Go back to home screen
                    }
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  IconData _getCategoryIcon(String category) {
    switch (category) {
      case 'Food': return Icons.restaurant;
      case 'Transport': return Icons.directions_car;
      case 'Shopping': return Icons.shopping_bag;
      case 'Entertainment': return Icons.movie;
      case 'Utilities': return Icons.bolt;
      default: return Icons.category;
    }
  }

  Color _getCategoryColor(String category) {
    final colors = [
      Colors.blue, Colors.red, Colors.green, 
      Colors.orange, Colors.purple, Colors.teal
    ];
    return colors[category.hashCode % colors.length];
  }
}