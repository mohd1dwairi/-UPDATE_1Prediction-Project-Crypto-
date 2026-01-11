import api from "./api";

export const login = async ({ email, password }) => {
  const loginData = {
    email: email, 
    password: password,
  };

  const response = await api.post("/auth/login", loginData, {
    headers: {
      "Content-Type": "application/json",
    },
  });

  return response.data; 
};

export const logout = () => {
  localStorage.removeItem("user_token");
};
