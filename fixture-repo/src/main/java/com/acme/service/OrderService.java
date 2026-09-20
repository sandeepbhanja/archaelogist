package com.acme.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.acme.dao.OrderDao;

@Service
public class OrderService {

    @Autowired
    private OrderDao orderDao;

    public void cancelOrder(long orderId) {
        Order order = orderDao.findById(orderId);
        if (order == null) {
            throw new IllegalArgumentException("Order not found: " + orderId);
        }
        order.setStatus("CANCELLED");
        orderDao.update(order);
        notifyCancellation(orderId);
    }

    private void notifyCancellation(long orderId) {
        // TODO: wire up actual notification service
        System.out.println("Order cancelled: " + orderId);
    }

    public Order getOrder(long orderId) {
        return orderDao.findById(orderId);
    }
}
