package com.acme.dao;

public interface OrderDao {
    Order findById(long orderId);
    void update(Order order);
}
