import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';

class CategoryScreen extends StatefulWidget {
  @override
  _CategoryScreenState createState() => _CategoryScreenState();
}

class _CategoryScreenState extends State<CategoryScreen> {
  final _formKey = GlobalKey<FormState>();
  String? _category;
  double? _budget;

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<TransactionProvider>(context);
    return Scaffold(
      appBar: AppBar(
        title: Text('Manage Categories'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Form(
              key: _formKey,
              child: Column(
                children: [
                  TextFormField(
                    decoration: InputDecoration(labelText: 'Category Name'),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter a category name';
                      }
                      return null;
                    },
                    onSaved: (value) => _category = value,
                  ),
                  TextFormField(
                    decoration: InputDecoration(labelText: 'Budget (Optional)'),
                    keyboardType: TextInputType.number,
                    onSaved: (value) => _budget = double.tryParse(value ?? '0'),
                  ),
                  SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: () {
                      if (_formKey.currentState!.validate()) {
                        _formKey.currentState!.save();
                        provider.setBudget(_category!, _budget ?? 0);
                        _formKey.currentState!.reset();
                      }
                    },
                    child: Text('Add Category'),
                  ),
                ],
              ),
            ),
            Expanded(
              child: ListView.builder(
                itemCount: provider.budgets.length,
                itemBuilder: (context, index) {
                  final category = provider.budgets.keys.elementAt(index);
                  final budget = provider.budgets[category];
                  return ListTile(
                    title: Text(category),
                    subtitle: Text('Budget: \$${budget?.toStringAsFixed(2)}'),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}