import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';
import '../utils/responsive.dart';

class BudgetScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final responsive = Responsive(context);
    final provider = Provider.of<TransactionProvider>(context);
    
    return Scaffold(
      appBar: AppBar(title: Text('Budget Planner')),
      body: Padding(
        padding: EdgeInsets.symmetric(
          horizontal: responsive.responsiveValue(mobile: 16, tablet: 32),
          vertical: 16,
        ),
        child: Column(
          children: [
            _buildBudgetHeader(context, responsive),
            SizedBox(height: 24),
            Expanded(
              child: ListView.builder(
                itemCount: provider.budgets.length,
                itemBuilder: (context, index) {
                  final category = provider.budgets.keys.elementAt(index);
                  final budget = provider.budgets[category]!;
                  final spending = _calculateCategorySpending(provider, category);
                  final percentage = spending / budget;
                  
                  return Card(
                    margin: EdgeInsets.only(bottom: 16),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                category,
                                style: TextStyle(
                                  fontSize: responsive.responsiveValue(mobile: 16, tablet: 18),
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                '\$${spending.toStringAsFixed(2)} / \$${budget.toStringAsFixed(2)}',
                                style: TextStyle(
                                  fontSize: responsive.responsiveValue(mobile: 14, tablet: 16),
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 8),
                          LinearProgressIndicator(
                            value: percentage > 1 ? 1 : percentage,
                            backgroundColor: Colors.grey[200],
                            color: percentage > 0.8 
                                ? percentage > 1 ? Colors.red : Colors.orange 
                                : Colors.green,
                            minHeight: responsive.responsiveValue(mobile: 8, tablet: 12),
                          ),
                          SizedBox(height: 8),
                          Text(
                            '${(percentage * 100).toStringAsFixed(1)}% of budget',
                            style: TextStyle(
                              fontSize: responsive.responsiveValue(mobile: 12, tablet: 14),
                              color: Colors.grey,
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBudgetHeader(BuildContext context, Responsive responsive) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          'Category Budgets',
          style: TextStyle(
            fontSize: responsive.responsiveValue(mobile: 20, tablet: 24),
            fontWeight: FontWeight.bold,
          ),
        ),
        IconButton(
          icon: Icon(Icons.add_chart),
          onPressed: () => _addNewBudget(context),
          iconSize: responsive.responsiveValue(mobile: 24, tablet: 28),
        ),
      ],
    );
  }
}

double _calculateCategorySpending(TransactionProvider provider, String category) {
    return provider.transactions
        .where((t) => !t.isIncome && t.category == category)
        .fold(0.0, (sum, item) => sum + item.amount);
}

void _addNewBudget(BuildContext context) {
    // Implement logic to add a new budget
    // This could open a dialog or navigate to a new screen
    showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
            title: Text('Add New Budget'),
            content: Text('This feature is not yet implemented.'),
            actions: <Widget>[
                TextButton(
                    child: Text('Okay'),
                    onPressed: () {
                        Navigator.of(ctx).pop();
                    },
                )
            ],
        ),
    );
}