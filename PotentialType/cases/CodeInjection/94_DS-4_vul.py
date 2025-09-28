    def vulnerable_calculate(self, product_type: str, discount_logic: str, quantity: int):
        try:
            base_price = self.base_prices.get(product_type, 0)
            # Vulnerable code injection in discount calculation
            discount = eval(discount_logic, {'math': math, 'quantity': quantity})  # Injection point
            return base_price * quantity * (1 - discount)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))