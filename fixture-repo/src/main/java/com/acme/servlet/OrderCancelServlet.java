package com.acme.servlet;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import com.acme.dao.OrderDaoImpl;

public class OrderCancelServlet extends HttpServlet {

    private OrderDaoImpl orderDao = new OrderDaoImpl();

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        long orderId = Long.parseLong(req.getParameter("orderId"));

        boolean success = orderDao.cancelOrderDirect(orderId);

        if (success) {
            resp.setStatus(200);
            resp.getWriter().write("Order cancelled: " + orderId);
        } else {
            resp.setStatus(404);
            resp.getWriter().write("Order not found: " + orderId);
        }
    }
}
